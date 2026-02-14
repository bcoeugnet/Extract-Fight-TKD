#!/usr/bin/env python3
"""
Improved PDF Parser for Taekwondo Competition
Accurately extracts fighters and fights for CLUB ATHLETIQUE
"""

import pdfplumber
import re
import json

TARGET_CLUB = "CLUB ATHLETIQUE"


def parse_pdf_for_club(pdf_path):
    """Parse PDF and extract club fighters with their fights
    
    Note: The same matchup may appear with multiple fight numbers because:
    - Tournament brackets can show the same pair at different stages
    - The PDF may reference the same fight from different pages
    - Fight numbers in different rounds of the bracket may overlap
    
    The website handles this by deduplicating based on fight_number.
    """
    
    club_fighters = []
    all_fights = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text or TARGET_CLUB not in text:
                continue
            
            lines = text.split('\n')
            
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
                fighter_matches = list(re.finditer(
                    r'\(([BR])-(\d+)\)\s+([A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸ][A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸa-zàâæçéèêëïîôœùûüÿ\s\-]+?)(?=\s+[BR]-\.\.|FRA|\s+\(|\s*$)',
                    fighter_line
                ))
                
                if not fighter_matches:
                    continue
                
                # Determine which fighters belong to CLUB ATHLETIQUE
                if club_count == 2:
                    # Both fighters are from CLUB ATHLETIQUE
                    for match in fighter_matches:
                        club_fighters.append({
                            'name': match.group(3).strip(),
                            'number': match.group(2),
                            'registration_color': 'Blue' if match.group(1) == 'B' else 'Red',
                            'page': page_num
                        })
                
                elif club_count == 1 and len(fighter_matches) >= 2:
                    # Only one club is CLUB ATHLETIQUE - determine which fighter
                    # Split the club line to find positions
                    club_pos = line.find(TARGET_CLUB)
                    line_midpoint = len(line) // 2
                    
                    # If CLUB ATHLETIQUE is in second half, it's the second fighter
                    # If in first half, it's the first fighter
                    our_fighter_idx = 1 if club_pos > line_midpoint else 0
                    
                    if our_fighter_idx < len(fighter_matches):
                        match = fighter_matches[our_fighter_idx]
                        club_fighters.append({
                            'name': match.group(3).strip(),
                            'number': match.group(2),
                            'registration_color': 'Blue' if match.group(1) == 'B' else 'Red',
                            'page': page_num
                        })
                
                # Now extract fight numbers - look for 3-digit numbers around this area
                fight_nums = []
                for offset in range(-3, 3):
                    if 0 <= i + offset < len(lines):
                        nums = re.findall(r'\b(\d{3})\b', lines[i + offset])
                        fight_nums.extend(nums)
                
                # Store fight information with both fighters if we have them
                if len(fighter_matches) >= 2 and fight_nums:
                    for fight_num in fight_nums:
                        # Avoid duplicates - skip numbers that look like IDs (> 400)
                        if int(fight_num) > 400:
                            continue
                        
                        f1 = fighter_matches[0]
                        f2 = fighter_matches[1]
                        
                        all_fights.append({
                            'fight_number': fight_num,
                            'fighter1': {
                                'name': f1.group(3).strip(),
                                'number': f1.group(2),
                                'registration_color': 'Blue' if f1.group(1) == 'B' else 'Red'
                            },
                            'fighter2': {
                                'name': f2.group(3).strip(),
                                'number': f2.group(2),
                                'registration_color': 'Blue' if f2.group(1) == 'B' else 'Red'
                            },
                            'page': page_num
                        })
    
    # Remove duplicate fighters
    unique_fighters = {}
    for fighter in club_fighters:
        if fighter['number'] not in unique_fighters:
            unique_fighters[fighter['number']] = fighter
    
    fighters_list = list(unique_fighters.values())
    
    # Filter fights to only those involving our club
    club_numbers = {f['number'] for f in fighters_list}
    relevant_fights = []
    seen_fights = set()
    
    for fight in all_fights:
        f1_num = fight['fighter1']['number']
        f2_num = fight['fighter2']['number']
        fight_num = fight['fight_number']
        
        # Check if at least one fighter is from our club
        if f1_num in club_numbers or f2_num in club_numbers:
            # Avoid duplicates
            fight_key = fight_num
            if fight_key not in seen_fights:
                seen_fights.add(fight_key)
                fight['our_fighter1'] = f1_num in club_numbers
                fight['our_fighter2'] = f2_num in club_numbers
                relevant_fights.append(fight)
    
    return fighters_list, relevant_fights


def main():
    # Note: The PDF filename actually contains two consecutive dots (..)
    # This is the original filename from the competition organizers
    pdf_path = "Tirages..pdf"
    
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
