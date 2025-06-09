import csv
import os

def convert_training_data():
    """Convert training_data.csv from old format to new format."""
    models_dir = os.path.join(os.getcwd(), 'models', 'sentiment_analysis')
    training_file = os.path.join(models_dir, 'training_data.csv')
    backup_file = os.path.join(models_dir, 'training_data_backup.csv')
    
    print(f"Converting file: {training_file}")
    
    # Create backup
    if os.path.exists(training_file):
        import shutil
        shutil.copy2(training_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    # Read old format (tab-separated)
    converted_data = []
    with open(training_file, 'r', encoding='utf-8') as csvfile:
        # Use tab as delimiter for the old format
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            text = row.get('tweets_descriptions', '').strip()
            sentiment = row.get('tweets_classification', '').strip().lower()
            
            if text and sentiment:
                converted_data.append([text, sentiment])
                print(f"Converting: '{text[:50]}...' -> {sentiment}")
    
    print(f"Found {len(converted_data)} records to convert")
    
    # Write new format (comma-separated)
    with open(training_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['text', 'sentiment'])
        writer.writerows(converted_data)
    
    print(f"Successfully converted {len(converted_data)} records to new format")
    print(f"New file format: text,sentiment")

if __name__ == "__main__":
    convert_training_data() 