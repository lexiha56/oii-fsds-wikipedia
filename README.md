# oii-fsds-wikipedia
A repository for downloading and analyzing Wikipedia revisions. Used in Fundamentals of Social Data Science for the MSc Social Data Science at the Oxford Internet Institute.

## Installation
The dependencies can be installed using `pip`:
```bash
pip install .
```

NB: Remember to use some kind of virtual environment to avoid a world of pain!

## Usage
This repository contains two main scripts for working with Wikipedia revisions:

### 1. Downloading Revisions
The script `download_wiki_revisions.py` downloads all revisions of a given Wikipedia page and organizes them into a directory structure by year and month. Usage:
```bash
usage: download_wiki_revisions.py [-h] [--data-dir DATA_DIR] [--count-only] page

Download Wikipedia page revisions

positional arguments:
  page                   Title of the Wikipedia page

options:
  -h, --help            show this help message and exit
  --data-dir DATA_DIR   Directory to store the revision data (default: data)
  --count-only          Only count and display stored revisions without downloading
```

The script will create a directory structure like:
```
data/
  ArticleName/
    2023/
      01/
        revision1.xml
        revision2.xml
      02/
        ...
```

### 2. Converting to DataFrames
The script `xml_to_dataframe.py` converts the downloaded XML files into pandas DataFrames and saves them in Feather format. Usage:
```bash
usage: xml_to_dataframe.py [-h] --data-dir DATA_DIR [--output-dir OUTPUT_DIR]
                          [--batch-size BATCH_SIZE] [--include-text]

Convert Wikipedia revision XMLs to DataFrames

options:
  -h, --help            show this help message and exit
  --data-dir DATA_DIR   Directory containing article revision directories
  --output-dir OUTPUT_DIR
                        Directory to save DataFrame files (default: DataFrames)
  --batch-size BATCH_SIZE
                        Number of files to process in each batch (default: 1000)
  --include-text        Include full text content in the DataFrame (significantly increases file size)
```

The script creates one Feather file per article:
```
DataFrames/
  ArticleName.feather
```

Each DataFrame contains the following columns:
- revision_id: Unique identifier for each revision
- timestamp: When the revision was made
- username: Editor's username
- userid: Editor's ID
- comment: Edit comment
- text_length: Length of the revision content
- year: Year of the revision
- month: Month of the revision
- text: Full revision content (only if --include-text is used)

## Example Workflow
1. Download revisions for multiple articles:
```bash
python download_wiki_revisions.py "Data_science"
python download_wiki_revisions.py "Machine_learning"
```

2. Convert all downloaded revisions to DataFrames:
```bash
python xml_to_dataframe.py --data-dir ./data --output-dir ./DataFrames
```

3. Or include full text content (requires more storage):
```bash
python xml_to_dataframe.py --data-dir ./data --output-dir ./DataFrames --include-text
```
