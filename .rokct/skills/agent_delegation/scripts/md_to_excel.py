# Licensed under the MIT License.
# Copyright 2024 RokctAI

import os
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# --- GLOBAL THEMES ---
INDIGO_HEADER = "4B0082"
EMERALD_HEADER = "50C878"
RUBY_HEADER = "E0115F"  # For Tenders
TEXT_WHITE = "FFFFFF"
STRIPE_GRAY = "F2F2F2"

def apply_premium_style(writer, sheet_name, header_color):
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    header_fill = PatternFill(start_color=header_color, end_color=header_color, fill_type="solid")
    header_font = Font(bold=True, color=TEXT_WHITE)
    stripe_fill = PatternFill(start_color=STRIPE_GRAY, end_color=STRIPE_GRAY, fill_type="solid")
    
    # 1. Style Header
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # 2. Zebra Stripes & Filters
    rows = list(worksheet.rows)
    for i, row in enumerate(rows[1:], start=2):
        if i % 2 == 0:
            for cell in row:
                cell.fill = stripe_fill
    
    # 3. Freeze Top Row
    worksheet.freeze_panes = "A2"
    
    # 4. Auto-Filter
    worksheet.auto_filter.ref = worksheet.dimensions

    # 5. Auto-Column Width
    for col_idx in range(1, worksheet.max_column + 1):
        max_length = 0
        column = get_column_letter(col_idx)
        for cell in worksheet[column]:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        worksheet.column_dimensions[column].width = adjusted_width

def parse_markdown_table(md_content):
    lines = md_content.split('\n')
    table_lines = [l.strip() for l in lines if l.strip().startswith('|')]
    if len(table_lines) < 2: return None
    
    # Skip separator row
    clean_lines = [l for l in table_lines if not re.match(r'^\|\s*[:\-|\s]+\s*\|$', l)]
    
    rows = []
    for line in clean_lines:
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        rows.append(cells)
    
    if len(rows) < 2: return None
    return pd.DataFrame(rows[1:], columns=rows[0])

def parse_discrete_markdown(md_content):
    data = {}
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    data['Grant Title'] = title_match.group(1).strip() if title_match else "Unknown"
    
    fields = {
        'Organization': r'-\s+\*\*Organization\*\*:\s*(.+)$',
        'Deadline': r'-\s+\*\*Deadline\*\*:\s*(.+)$',
        'Amount': r'-\s+\*\*Funding Amount\*\*:\s*(.+)$',
        'Focus Area': r'-\s+\*\*Focus Area\*\*:\s*(.+)$',
        'Apply Link': r'-\s+\*\*Applying Link\*\*:\s*(.+)$',
        'Source': r'-\s+\*\*Source\*\*:\s*(.+)$',
        'Status': r'-\s+\*\*Verification Status\*\*:\s*(.+)$'
    }
    for label, pattern in fields.items():
        match = re.search(pattern, md_content, re.MULTILINE)
        data[label] = match.group(1).strip() if match else ""
    return data

def is_expired(deadline_str):
    if not deadline_str or "Ongoing" in deadline_str: return False
    try:
        # Expected format: YYYY-MM-DD
        deadline_date = datetime.strptime(deadline_str[:10], '%Y-%m-%d')
        return deadline_date < datetime.now()
    except:
        return False

def parse_tender_markdown(md_content):
    """Parses individual tender files based on the detailed template."""
    data = {}
    title_match = re.search(r'^#\s+Tender Opportunity:\s*(.+)$', md_content, re.MULTILINE)
    data['Tender Title'] = title_match.group(1).strip() if title_match else "Unknown"
    
    # Extract Category from the section below ### Category
    cat_match = re.search(r'### Category\s*\n\s*(.+)', md_content)
    data['Category'] = cat_match.group(1).strip() if cat_match else "Uncategorized"

    fields = {
        'Tender Number': r'-\s+\*\*Tender Number\*\*:\s*(.+)$',
        'Institution': r'-\s+\*\*Institution\*\*:\s*(.+)$',
        'Type': r'-\s+\*\*Tender Type\*\*:\s*(.+)$',
        'Closing Date': r'-\s+\*\*Closing Date\*\*:\s*(.+)$',
        'Applying Link': r'-\s+\*\*Applying Link\*\*:\s*(.+)$',
        'Status': r'-\s+\*\*Status\*\*:\s*(.+)$'
    }
    for label, pattern in fields.items():
        match = re.search(pattern, md_content, re.MULTILINE)
        data[label] = match.group(1).strip() if match else ""
    return data

def clean_filename(name):
    """Sanitizes names for Excel sheet constraints."""
    return re.sub(r'[\\/*?:\[\]]', '', name)

def sync_md_to_excel():
    equity_dir = Path('01_equity')
    grants_dir = Path('02_grants')
    tenders_dir = Path('03_tenders')
    pub_dir = Path('published')
    pub_dir.mkdir(parents=True, exist_ok=True)
    
    # --- 1. PROCESS EQUITY ---
    if equity_dir.exists():
        equity_dfs = []
        for md_file in equity_dir.glob('*.md'):
            if md_file.name in ['registry_audit_log.md', 'global_audit_log.md']: continue
            with open(md_file, 'r', encoding='utf-8') as f:
                df = parse_markdown_table(f.read())
                if df is not None: equity_dfs.append(df)
        
        if equity_dfs:
            full_equity = pd.concat(equity_dfs, ignore_index=True)
            
            # --- VERIFICATION FILTER ---
            # For Equity, we prioritize a 'Status' column if it exists.
            # If not, we ensure 'Source / Verification' has meaningful content.
            if 'Status' in full_equity.columns:
                full_equity = full_equity[full_equity['Status'].str.upper().isin(['ACTIVE', 'VERIFIED', ''])]
            elif 'Source / Verification' in full_equity.columns:
                # Ensure it's not just empty or "N/A"
                full_equity = full_equity[
                    full_equity['Source / Verification'].fillna('').str.len() > 3
                ]

            # Geographic Filters
            def is_sa(row):
                val = (str(row.get('Country', '')) + " " + str(row.get('Territory', ''))).lower()
                return 'south africa' in val
            
            def is_africa(row):
                val = (str(row.get('Country', '')) + " " + str(row.get('Territory', ''))).lower()
                # Simple list of major African identifiers
                african_keywords = ['africa', 'kenya', 'nigeria', 'egypt', 'ghana', 'ethiopia', 'rwanda', 'uganda']
                return any(kw in val for kw in african_keywords)

            # SAVE EQUITY GLOBAL
            with pd.ExcelWriter(str(pub_dir / '01_Equity_Global.xlsx'), engine='openpyxl') as writer:
                full_equity.to_excel(writer, sheet_name='Global_Funders', index=False)
                apply_premium_style(writer, 'Global_Funders', INDIGO_HEADER)
                
            # SAVE EQUITY SOUTH AFRICA
            df_sa = full_equity[full_equity.apply(is_sa, axis=1)]
            with pd.ExcelWriter(str(pub_dir / '01_Equity_SouthAfrica.xlsx'), engine='openpyxl') as writer:
                df_sa.to_excel(writer, sheet_name='SA_Focus', index=False)
                apply_premium_style(writer, 'SA_Focus', INDIGO_HEADER)
                
            # SAVE EQUITY AFRICA
            df_africa = full_equity[full_equity.apply(is_africa, axis=1)]
            with pd.ExcelWriter(str(pub_dir / '01_Equity_Africa.xlsx'), engine='openpyxl') as writer:
                df_africa.to_excel(writer, sheet_name='Africa_Focus', index=False)
                apply_premium_style(writer, 'Africa_Focus', INDIGO_HEADER)

    # --- 2. PROCESS GRANTS ---
    if grants_dir.exists():
        active_grants = []
        for md_file in grants_dir.glob('*.md'):
            if md_file.name in ['template.md']: continue
            with open(md_file, 'r', encoding='utf-8') as f:
                data = parse_discrete_markdown(f.read())
                # Only include ACTIVE/VERIFIED grants that are not expired
                status = data.get('Status', '').upper()
                is_valid = status in ['ACTIVE', 'VERIFIED']
                if data and is_valid and not is_expired(data.get('Deadline', '')):
                    active_grants.append(data)
        
        if active_grants:
            df_grants = pd.DataFrame(active_grants)
            with pd.ExcelWriter(str(pub_dir / '02_Grants_Active.xlsx'), engine='openpyxl') as writer:
                df_grants.to_excel(writer, sheet_name='Active_Grants', index=False)
                apply_premium_style(writer, 'Active_Grants', EMERALD_HEADER)

    # --- 3. PROCESS TENDERS ---
    if tenders_dir.exists():
        all_tenders = []
        for md_file in tenders_dir.glob('*.md'):
            if md_file.name in ['template.md', 'registry_audit_log.md']: continue
            with open(md_file, 'r', encoding='utf-8') as f:
                data = parse_tender_markdown(f.read())
                # Only include ACTIVE tenders
                if data and data.get('Status', '').upper() == 'ACTIVE':
                    all_tenders.append(data)
        
        if all_tenders:
            df_tenders = pd.DataFrame(all_tenders)
            with pd.ExcelWriter(str(pub_dir / '03_Tenders_Master.xlsx'), engine='openpyxl') as writer:
                # Group by category and save each as a sheet
                for category, group in df_tenders.groupby('Category'):
                    sheet_name = clean_filename(category)[:31] # Excel limit
                    group.to_excel(writer, sheet_name=sheet_name, index=False)
                    apply_premium_style(writer, sheet_name, RUBY_HEADER)

    print("Premium Registry Expansion Complete.")

if __name__ == "__main__":
    sync_md_to_excel()
