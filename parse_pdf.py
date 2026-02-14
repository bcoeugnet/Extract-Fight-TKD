#!/usr/bin/env python3
"""
PDF Parser for Taekwondo Competition Brackets
Extracts fight information for fighters from specific clubs
"""

import pdfplumber
import re
import json

TARGET_CLUB = "CLUB ATHLETIQUE"


def extract_fighter_info(text):
    """Extract fighter information from text lines"""
    fighters = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        # Look for lines containing TARGET_CLUB
        if TARGET_CLUB in line:
            # The fighter line is typically 1-2 lines before the club line
            # Look for fighter name in previous lines
            for offset in [1, 2, 3]:
                if i - offset >= 0:
                    fighter_line = lines[i - offset]
                    # Find all fighters in this line - can be multiple on same line
                    matches = re.findall(r'\((B|R)-(\d+)\)\s+([A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸ][A-ZÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸa-zàâæçéèêëïîôœùûüÿ\s\-]+?)(?=\s+\(|$|FRA)', fighter_line)
                    
                    for match in matches:
                        color = match[0]
                        number = match[1]
                        name = match[2].strip()
                        
                        # Determine which side of the line this club appears on
                        # Split the club line to see if it's on the left or right
                        parts = line.split(TARGET_CLUB)
                        
                        # If the club appears and this is a valid fighter name
                        if name and len(name) > 1:
                            fighters.append({
                                'name': name,
                                'color': 'Blue' if color == 'B' else 'Red',
                                'fighter_number': number,
                                'club': TARGET_CLUB
                            })
    
    return fighters


def extract_fight_numbers(text):
    """Extract fight numbers from text"""
    fight_numbers = re.findall(r'\b(\d{3})\b', text)
    return fight_numbers


def parse_pdf(pdf_path):
    """Parse the PDF and extract all relevant information"""
    all_fighters = []
    all_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text += f"\n--- PAGE {page_num + 1} ---\n{text}"
                fighters = extract_fighter_info(text)
                for fighter in fighters:
                    fighter['page'] = page_num + 1
                all_fighters.extend(fighters)
    
    # Remove duplicates based on fighter_number
    seen = set()
    unique_fighters = []
    for fighter in all_fighters:
        if fighter['fighter_number'] not in seen:
            seen.add(fighter['fighter_number'])
            unique_fighters.append(fighter)
    
    return unique_fighters, all_text


def main():
    pdf_path = "Tirages..pdf"
    fighters, full_text = parse_pdf(pdf_path)
    
    print(f"Found {len(fighters)} fighters from {TARGET_CLUB}:")
    print(json.dumps(fighters, indent=2))
    
    # Save to JSON file
    with open('fighters_data.json', 'w', encoding='utf-8') as f:
        json.dump(fighters, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to fighters_data.json")


if __name__ == "__main__":
    main()
