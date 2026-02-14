#!/usr/bin/env python3
"""
Enhanced PDF Parser for Taekwondo Competition Brackets
Extracts fight information including brackets and potential future matches
"""

import pdfplumber
import re
import json

TARGET_CLUB = "CLUB ATHLETIQUE"


def extract_all_fights_on_page(text, page_num):
    """Extract all fights from a page"""
    fights = []
    lines = text.split('\n')
    
    # Look for fight numbers (3 digits)
    for i, line in enumerate(lines):
        # Find fight numbers - typically standalone 3-digit numbers
        fight_matches = re.finditer(r'\b(\d{3})\b', line)
        
        for match in fight_matches:
            fight_num = match.group(1)
            
            # Look for fighters around this fight number
            # Fighters are usually 1-3 lines before the fight number
            context_start = max(0, i - 5)
            context_end = min(len(lines), i + 2)
            context = '\n'.join(lines[context_start:context_end])
            
            # Extract fighters from context
            fighter_matches = re.findall(
                r'\((B|R)-(\d+)\)\s+([A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸ][A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸa-zàâæçéèêëïîôœùûüÿ\s\-]+?)(?=\s+\(|FRA|$)',
                context
            )
            
            if len(fighter_matches) >= 2:
                # Typically two fighters per match
                blue_fighter = None
                red_fighter = None
                
                for fm in fighter_matches:
                    color_code = fm[0]
                    fighter_num = fm[1]
                    fighter_name = fm[2].strip()
                    
                    if color_code == 'B' and not blue_fighter:
                        blue_fighter = {
                            'number': fighter_num,
                            'name': fighter_name,
                            'color': 'Blue'
                        }
                    elif color_code == 'R' and not red_fighter:
                        red_fighter = {
                            'number': fighter_num,
                            'name': fighter_name,
                            'color': 'Red'
                        }
                
                if blue_fighter and red_fighter:
                    fights.append({
                        'fight_number': fight_num,
                        'blue_fighter': blue_fighter,
                        'red_fighter': red_fighter,
                        'page': page_num
                    })
    
    return fights


def extract_club_fighters_and_fights(pdf_path):
    """Extract all fighters from TARGET_CLUB and their associated fights"""
    club_fighters = []
    all_fights = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            # Extract club fighters
            for i, line in enumerate(lines):
                if TARGET_CLUB in line:
                    # Look for fighters 1-3 lines before
                    for offset in [1, 2, 3]:
                        if i - offset >= 0:
                            fighter_line = lines[i - offset]
                            matches = re.findall(
                                r'\((B|R)-(\d+)\)\s+([A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸ][A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸa-zàâæçéèêëïîôœùûüÿ\s\-]+?)(?=\s+\(|$|FRA)',
                                fighter_line
                            )
                            
                            for match in matches:
                                color = match[0]
                                number = match[1]
                                name = match[2].strip()
                                
                                if name and len(name) > 1:
                                    club_fighters.append({
                                        'name': name,
                                        'color': 'Blue' if color == 'B' else 'Red',
                                        'number': number,
                                        'club': TARGET_CLUB,
                                        'page': page_num
                                    })
            
            # Extract all fights from this page
            page_fights = extract_all_fights_on_page(text, page_num)
            all_fights.extend(page_fights)
    
    # Remove duplicate fighters
    seen_fighters = {}
    for fighter in club_fighters:
        if fighter['number'] not in seen_fighters:
            seen_fighters[fighter['number']] = fighter
    
    unique_fighters = list(seen_fighters.values())
    
    # Find fights involving club fighters
    club_fighter_numbers = {f['number'] for f in unique_fighters}
    relevant_fights = []
    
    for fight in all_fights:
        blue_num = fight['blue_fighter']['number']
        red_num = fight['red_fighter']['number']
        
        if blue_num in club_fighter_numbers or red_num in club_fighter_numbers:
            # Mark which fighter is from our club
            fight['club_fighter_blue'] = blue_num in club_fighter_numbers
            fight['club_fighter_red'] = red_num in club_fighter_numbers
            relevant_fights.append(fight)
    
    return unique_fighters, relevant_fights


def main():
    pdf_path = "Tirages..pdf"
    fighters, fights = extract_club_fighters_and_fights(pdf_path)
    
    print(f"Found {len(fighters)} fighters from {TARGET_CLUB}")
    print(f"Found {len(fights)} fights involving these fighters")
    
    # Create comprehensive data structure
    data = {
        'club': TARGET_CLUB,
        'fighters': fighters,
        'fights': fights,
        'fight_results': {}  # To be updated with win/loss status
    }
    
    # Save to JSON
    with open('fight_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\nFighters:")
    for f in fighters:
        print(f"  {f['number']}: {f['name']} ({f['color']})")
    
    print("\nFights:")
    for fight in fights:
        marker_blue = "★" if fight['club_fighter_blue'] else " "
        marker_red = "★" if fight['club_fighter_red'] else " "
        print(f"  Fight {fight['fight_number']}: {marker_blue}{fight['blue_fighter']['name']} (B) vs {marker_red}{fight['red_fighter']['name']} (R)")
    
    print(f"\nData saved to fight_data.json")


if __name__ == "__main__":
    main()
