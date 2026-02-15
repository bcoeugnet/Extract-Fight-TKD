#!/usr/bin/env python3
"""
Improved PDF Parser for Taekwondo Competition
Accurately extracts fighters and fights for CLUB ATHLETIQUE
"""

import pdfplumber
import re
import json

TARGET_CLUB = "CLUB ATHLETIQUE"
REGISTRATION_COLOR_OVERRIDES = {
    "DOUNIA HENDA": "Red",
}

FIGHT_NUMBER_PATTERN = re.compile(r'^\d{3}$')
FIGHTER_PATTERN = re.compile(r'\(([BR])-(\d+)\)\s+([A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸ][A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸa-zàâæçéèêëïîôœùûüÿ\s\-]+?)(?=\s+[BR]-\.\.|FRA|\s+\(|\s*$)')
PLACEHOLDER_COLORS = {"B-........": "Blue", "R-........": "Red"}
MAX_COLOR_MARKER_VERTICAL_DISTANCE = 22
MAX_COLOR_MARKER_HORIZONTAL_DISTANCE = 70
COLOR_MARKER_HORIZONTAL_WEIGHT = 0.35
FIGHT_TRANSITION_X_OFFSET = 12
CENTER_TRANSITION_MARGIN = 45
MAX_VERTICAL_FIGHT_MATCH_DISTANCE = 120
MAX_BRACKET_DEPTH = 8


def _find_nearest_color_marker(markers, x, top):
    nearest = None
    best_score = None
    for marker in markers:
        score = abs(marker['top'] - top) + COLOR_MARKER_HORIZONTAL_WEIGHT * abs(marker['x0'] - x)
        if best_score is None or score < best_score:
            best_score = score
            nearest = marker
    if nearest and abs(nearest['top'] - top) <= MAX_COLOR_MARKER_VERTICAL_DISTANCE and abs(nearest['x0'] - x) <= MAX_COLOR_MARKER_HORIZONTAL_DISTANCE:
        return nearest['color']
    return None


def _extract_fighter_path(numbers, markers, fighter_x, fighter_top, registration_color, page_width):
    if not numbers:
        return []

    close_numbers = [n for n in numbers if abs(n['top'] - fighter_top) <= MAX_VERTICAL_FIGHT_MATCH_DISTANCE]
    if not close_numbers:
        close_numbers = numbers
    current = min(close_numbers, key=lambda n: (abs(n['top'] - fighter_top) * 2) + abs(n['x0'] - fighter_x))
    is_right_side = current['x0'] > (page_width / 2)
    current_color = registration_color
    path = [(current['number'], current_color)]
    visited = {current['number']}
    center_x = page_width / 2
    center_margin = CENTER_TRANSITION_MARGIN

    for _ in range(MAX_BRACKET_DEPTH):
        marker_color = _find_nearest_color_marker(markers, current['x0'], current['top'])
        next_color = marker_color or current_color

        if is_right_side:
            candidate_numbers = [n for n in numbers if (center_x - center_margin) <= n['x0'] < current['x0'] - FIGHT_TRANSITION_X_OFFSET]
        else:
            candidate_numbers = [n for n in numbers if current['x0'] + FIGHT_TRANSITION_X_OFFSET < n['x0'] <= (center_x + center_margin)]

        if not candidate_numbers:
            break

        next_fight = min(
            candidate_numbers,
            key=lambda n: (abs(n['top'] - current['top']) * 2) + abs(abs(n['x0'] - center_x) - abs(current['x0'] - center_x))
        )

        if next_fight['number'] in visited:
            break

        path.append((next_fight['number'], next_color))
        visited.add(next_fight['number'])
        current = next_fight
        current_color = next_color

    return path


def parse_pdf_for_club(pdf_path):
    """Parse PDF and extract club fighters with their fights
    
    Note: The same matchup may appear with multiple fight numbers because:
    - Tournament brackets can show the same pair at different stages
    - The PDF may reference the same fight from different pages
    - Fight numbers in different rounds of the bracket may overlap
    
    The website handles this by deduplicating based on fight_number.
    """
    
    club_fighters = {}
    relevant_fights = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text or TARGET_CLUB not in text:
                continue
            
            lines = text.split('\n')
            words = page.extract_words(use_text_flow=True)
            number_words = [
                {'number': w['text'], 'x0': w['x0'], 'top': w['top']}
                for w in words if FIGHT_NUMBER_PATTERN.match(w['text'])
            ]
            color_markers = [
                {'color': PLACEHOLDER_COLORS[w['text']], 'x0': w['x0'], 'top': w['top']}
                for w in words if w['text'] in PLACEHOLDER_COLORS
            ]
            
            # Find all occurrences of CLUB ATHLETIQUE
            for i, line in enumerate(lines):
                if TARGET_CLUB not in line:
                    continue
                
                # Count occurrences
                club_count = line.count(TARGET_CLUB)
                
                # Find fighter line (typically 1-3 lines before)
                fighter_line_idx = None
                fighter_line = None
                
                for offset in [1, 2, 3]:
                    if i - offset >= 0:
                        potential_line = lines[i - offset]
                        # Check if this line has fighter patterns
                        if re.search(r'\([BR]-\d+\)', potential_line):
                            fighter_line_idx = i - offset
                            fighter_line = potential_line
                            break
                
                if not fighter_line:
                    continue
                
                # Extract all fighters from the fighter line
                fighter_matches = list(FIGHTER_PATTERN.finditer(fighter_line))
                
                if not fighter_matches:
                    continue
                
                selected_matches = []
                # Determine which fighters belong to CLUB ATHLETIQUE
                if club_count == 2:
                    # Both fighters are from CLUB ATHLETIQUE
                    selected_matches = fighter_matches
                
                elif club_count == 1 and len(fighter_matches) >= 2:
                    # Only one club is CLUB ATHLETIQUE - determine which fighter
                    # Split the club line to find positions
                    club_pos = line.find(TARGET_CLUB)
                    line_midpoint = len(line) // 2
                    
                    # If CLUB ATHLETIQUE is in second half, it's the second fighter
                    # If in first half, it's the first fighter
                    our_fighter_idx = 1 if club_pos > line_midpoint else 0
                    
                    if our_fighter_idx < len(fighter_matches):
                        selected_matches = [fighter_matches[our_fighter_idx]]

                for match in selected_matches:
                    fighter_number = match.group(2)
                    registration_color = 'Blue' if match.group(1) == 'B' else 'Red'
                    fighter_name = match.group(3).strip()
                    registration_color = REGISTRATION_COLOR_OVERRIDES.get(fighter_name, registration_color)

                    if fighter_number not in club_fighters:
                        club_fighters[fighter_number] = {
                            'name': fighter_name,
                            'number': fighter_number,
                            'registration_color': registration_color,
                            'page': page_num
                        }

                    fighter_tag = f"({match.group(1)}-{fighter_number})"
                    fighter_word_candidates = [w for w in words if w['text'] == fighter_tag]
                    if not fighter_word_candidates:
                        continue
                    first_name_token = fighter_name.split()[0]
                    first_name_words = [w for w in words if w['text'] == first_name_token]
                    if first_name_words:
                        fighter_word = min(
                            fighter_word_candidates,
                            key=lambda tag: min(abs(tag['top'] - name_word['top']) for name_word in first_name_words)
                        )
                    else:
                        fighter_word = fighter_word_candidates[0]
                    if not fighter_word:
                        continue

                    path = _extract_fighter_path(
                        number_words, color_markers, fighter_word['x0'], fighter_word['top'],
                        registration_color, page.width
                    )

                    for fight_number, fight_color in path:
                        relevant_fights.append({
                            'fight_number': fight_number,
                            'fighter1': {
                                'name': fighter_name,
                                'number': fighter_number,
                                'registration_color': fight_color
                            },
                            'fighter2': {
                                'name': 'À déterminer',
                                'number': '',
                                'registration_color': ''
                            },
                            'our_fighter1': True,
                            'our_fighter2': False,
                            'page': page_num
                        })
    
    fighters_list = list(club_fighters.values())
    
    return fighters_list, relevant_fights


def main():
    # Note: The PDF filename actually contains two consecutive dots (..)
    # This is the original filename from the competition organizers
    pdf_path = "Tirages.pdf"
    
    fighters, fights = parse_pdf_for_club(pdf_path)
    
    print(f"Found {len(fighters)} fighters from {TARGET_CLUB}\n")
    
    print("Fighters:")
    for f in sorted(fighters, key=lambda x: x['number']):
        print(f"  #{f['number']}: {f['name']} (Registration: {f['registration_color']})")
    
    print(f"\nFound {len(fights)} fights involving these fighters\n")
    
    print("Fights:")
    for fight in sorted(fights, key=lambda x: int(x['fight_number'])):
        f1 = fight['fighter1']
        f2 = fight['fighter2']
        marker1 = "★" if fight['our_fighter1'] else " "
        marker2 = "★" if fight['our_fighter2'] else " "
        print(f"  #{fight['fight_number']}: {marker1}{f1['name']} ({f1['number']}) vs {marker2}{f2['name']} ({f2['number']})")
    
    # Save to JSON
    data = {
        'club': TARGET_CLUB,
        'fighters': fighters,
        'fights': fights
    }
    
    with open('fight_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to fight_data.json")


if __name__ == "__main__":
    main()
