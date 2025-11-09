# Dropshipping CLI Guide

## Overview

The Dropshipping application now includes a powerful command-line interface (CLI) with clean, table-based output instead of plain ASCII text. All technical logging has been separated from user-facing output for a better experience.

## Key Features

✨ **Table-formatted output** - All data displayed in beautiful, easy-to-read tables  
📊 **Clean UI** - Minimal, focused output without technical clutter  
📝 **Smart logging** - Technical details logged to files, user messages to console  
🎨 **Color-coded** - Important information highlighted with colors  
⚡ **Progress indicators** - Spinners for long-running operations  

## Installation

The CLI uses the following additional dependencies (already in requirements.txt):
- `click` - Command-line framework
- `rich` - Beautiful terminal output with tables
- `tabulate` - Alternative table formatting

Install dependencies:
```bash
pip install -r requirements.txt
```

## Available Commands

### 1. Batch Processing

Run a batch task for a specific configuration:

```bash
python cli.py batch <config_id>
```

**Example:**
```bash
python cli.py batch 1
```

**Output:**
```
⠋ Processing batch for config 1...
✓ Batch task completed for config 1
```

---

### 2. Import Product IDs

Import product IDs from an external XML source:

```bash
python cli.py import-products --url <url>
```

**Example:**
```bash
python cli.py import-products --url https://example.com/products.xml
```

**Output:**
```
⠋ Importing product IDs...
✓ Product IDs imported successfully
```

---

### 3. List Products

Display products for a configuration in a formatted table:

```bash
python cli.py list-products <config_id> [--limit N]
```

**Options:**
- `--limit` - Number of products to display (default: 10)

**Example:**
```bash
python cli.py list-products 1 --limit 5
```

**Output:**
```
                                Products (showing 5 of 127)
╭───────────────────────────────┬───────────────┬──────────────────┬─────┬────────┬────────┬────────╮
│ Name                          │ EAN           │ Category         │ Qty │  Price │ Margin │  Gross │
├───────────────────────────────┼───────────────┼──────────────────┼─────┼────────┼────────┼────────┤
│ Garden Tools Set Professional │ 5901234567890 │ Garden Equipment │  15 │  89.99 │ 20.00% │ 131.99 │
│ Solar LED Light Outdoor       │ 5901234567891 │ Garden Lighting  │  42 │  45.50 │ 25.00% │  71.09 │
│ Plant Pot Ceramic Large       │ 5901234567892 │ Garden Decor     │   8 │ 129.00 │ 18.00% │ 184.77 │
│ Watering System Automatic     │ 5901234567893 │ Irrigation       │  23 │ 199.99 │ 20.00% │ 293.99 │
│ Garden Hose 50m Premium       │ 5901234567894 │ Irrigation       │  31 │  79.99 │ 22.00% │ 118.47 │
╰───────────────────────────────┴───────────────┴──────────────────┴─────┴────────┴────────┴────────╯

Total products: 127
```

---

### 4. List Custom Margins

View all custom margins configured for a specific configuration:

```bash
python cli.py list-margins <config_id>
```

**Example:**
```bash
python cli.py list-margins 1
```

**Output:**
```
     Custom Margins (Total: 4)
╭───────────────┬────────╮
│ EAN           │ Margin │
├───────────────┼────────┤
│ 5901234567890 │ 20.00% │
│ 5901234567891 │ 25.00% │
│ 5901234567892 │ 18.00% │
│ 5901234567894 │ 22.00% │
╰───────────────┴────────╯
```

---

### 5. Set Product Margin

Update or set a margin for a specific product:

```bash
python cli.py set-margin <config_id> <ean> <margin>
```

**Parameters:**
- `config_id` - Configuration ID
- `ean` - Product EAN code
- `margin` - Margin as decimal (e.g., 0.25 for 25%)

**Example:**
```bash
python cli.py set-margin 1 5901234567890 0.25
```

**Output:**
```
✓ Margin set: EAN 5901234567890 → 25.00%
```

---

### 6. Configuration Info

Display configuration details:

```bash
python cli.py config-info <config_id>
```

**Example:**
```bash
python cli.py config-info 1
```

**Output:**
```
            Configuration: HomeGarden
╭────────────────┬──────────────────────────────────────╮
│ Config ID      │ 1                                    │
│ Name           │ HomeGarden                           │
│ URL            │ https://example.com/api/products.xml │
│ Default Margin │ 20.00%                               │
╰────────────────┴──────────────────────────────────────╯
```

---

### 7. List Product Mappings

View EAN to Product ID mappings:

```bash
python cli.py list-mappings
```

**Output:**
```
   Product Mappings (Total: 150)
╭───────────────┬────────────╮
│ EAN           │ Product ID │
├───────────────┼────────────┤
│ 5901234567890 │ PROD-1001  │
│ 5901234567891 │ PROD-1002  │
│ 5901234567892 │ PROD-1003  │
...
╰───────────────┴────────────╯

Showing 50 of 150 mappings
```

---

## Logging System

### Two-Tier Logging

The application now uses a sophisticated two-tier logging system:

#### 1. Technical Logger
- **Purpose:** Debug information, technical details, system operations
- **Location:** `app/logs/app.log`
- **Level:** DEBUG and above
- **Use for:** Troubleshooting, debugging, development

#### 2. User Logger
- **Purpose:** Clean, user-facing messages
- **Location:** Console output only
- **Level:** INFO and above
- **Use for:** Status updates, results, errors

### Log File Location

All technical logs are written to:
```
app/logs/app.log
```

The log directory is automatically created if it doesn't exist.

### Example Log Output

**Console (User Logger):**
```
✓ Batch task completed for config 1
✓ Product IDs imported successfully
```

**Log File (Technical Logger):**
```
2025-11-09 20:52:43 - technical.parser_manager - DEBUG - Parsing data for config: HomeGarden, default_margin: 0.2
2025-11-09 20:52:43 - technical.parser_manager - DEBUG - Loaded 15 custom margins
2025-11-09 20:52:44 - technical.parser_manager - DEBUG - Parsed XML to dataframe: 127 rows
2025-11-09 20:52:44 - technical.parser_manager - INFO - Processed 127 products for config_id=1
```

---

## Batch Scheduler Output

The batch scheduler (`batch.py`) also uses Rich tables for job execution summaries:

### Scheduled Jobs Display
```
                Scheduled Jobs
╭────────┬─────────────┬──────────────┬────────╮
│ Job ID │ Name        │ Schedule     │ Status │
├────────┼─────────────┼──────────────┼────────┤
│ 1      │ HomeGarden  │ 0 2 * * *    │ Active │
│ 2      │ ETL_import  │ 30 1 * * *   │ Active │
╰────────┴─────────────┴──────────────┴────────╯
```

### Job Execution Summary
```
    Job Execution Complete
╭──────────┬─────────────╮
│ Job ID   │ 1           │
│ Job Name │ HomeGarden  │
│ Status   │ ✓ Completed │
╰──────────┴─────────────╯
```

---

## Usage in Docker

When running in Docker containers, the CLI commands work the same way:

### Execute from the app container:
```bash
docker exec frontend python cli.py list-products 1
```

### Execute from the scheduler container:
```bash
docker exec job_scheduler python cli.py batch 1
```

---

## Error Handling

The CLI provides clear, color-coded error messages:

```bash
# Success
✓ Operation completed

# Error
✗ Error: Connection timeout

# Warning
⚠ No custom margins configured
```

---

## Tips

1. **Use `--help`** on any command to see detailed usage:
   ```bash
   python cli.py --help
   python cli.py list-products --help
   ```

2. **Limit output** for large datasets:
   ```bash
   python cli.py list-products 1 --limit 20
   ```

3. **Check logs** for technical details when troubleshooting:
   ```bash
   tail -f app/logs/app.log
   ```

4. **Version info**:
   ```bash
   python cli.py --version
   ```

---

## Migration from Old Output

### Before (Plain ASCII):
```
2025-11-09 20:52:43 - parser_manager - INFO - Running batch task for config_id: 1
2025-11-09 20:52:43 - parser_manager - INFO - Default margin: 0.2
2025-11-09 20:52:44 - ftp_connector - INFO - Attempt 1 of 5
2025-11-09 20:52:44 - ftp_connector - INFO - Calculating MD5 for local file: xml_result_1.xml
2025-11-09 20:52:44 - ftp_connector - INFO - Local MD5: 5d41402abc4b2a76b9719d911017c592
```

### After (Clean Tables):
```
⠋ Processing batch for config 1...
✓ Batch task completed for config 1
```

All technical details are now in `app/logs/app.log` instead of cluttering the console!

---

## Development

### Adding New Commands

To add a new CLI command, edit `app/cli.py`:

```python
@cli.command()
@click.argument('param')
def my_command(param):
    """Command description."""
    tech_logger.info(f"Technical details")
    
    # Your logic here
    
    console.print("[green]✓[/green] Success message")
```

### Using Loggers in Code

```python
from utils.logger import get_technical_logger, get_user_logger

tech_logger = get_technical_logger(__name__)
user_logger = get_user_logger(__name__)

# Technical details (goes to log file)
tech_logger.debug("Processing 127 rows")
tech_logger.info("Task completed")

# User-facing messages (goes to console)
user_logger.info("✓ Operation successful")
```

---

## Support

For issues or questions, check:
1. Log files in `app/logs/app.log`
2. Command help: `python cli.py <command> --help`
3. Docker container logs: `docker logs frontend` or `docker logs job_scheduler`
