import os
import re
import sys
import io

# ==============================================================================
# === FILE READING =============================================================

def openFile(filePath):
    try:
        return io.open(filePath, 'r', encoding='windows-1252')
    except:
        sys.stdout.write('Could not find file "{}"\n'.format(filePath))
        exit(1)

def getMatching(regex, input_string):
    search_result = re.search(regex, input_string)
    return search_result.group(1) if search_result else None


# ==============================================================================
# === EMAIL CLASS ==============================================================

class Email(object):
    def __init__(self):
        self.subject = None
        self.content_type = None
        self.body = None

    def reset(self):
        self.subject = None
        self.content_type = None
        self.body = None

    def getEmailData(self):
        return [
            self.subject or '',
            self.content_type or '',
            self.body or ''
        ]

    def hasNoSubject(self):
        return self.subject is None

    def hasNoContentType(self):
        return self.content_type is None

    def hasBody(self):
        return self.body is not None

    def isEmpty(self):
        [subject, content_type, body] = self.getEmailData()
        return not (subject or content_type or body)


# ==============================================================================
# === READ DATASET =============================================================

FRAUD_FIRST_HEADER_REGEX = '^From r  \w{3} \w{3} ( ?\d{1,2}) \d{2}:\d{2}:\d{2} \d{4}$'
BENIGN_FIRST_HEADER_REGEX = '^Message-ID: <(.*)>'

EMAIL_SUBJECT_REGEX = '^Subject: (.*)$'
EMAIL_CONTENT_TYPE_REGEX = '^Content-Type: ([\w\/\-]*);'
EMAIL_BODY_START_REGEX = '^(\n|\r\n)'

def readDataset(dataset_path, is_benign):
    if (is_benign):
        EMAIL_FIRST_HEADER_REGEX = BENIGN_FIRST_HEADER_REGEX
    else:
        EMAIL_FIRST_HEADER_REGEX = FRAUD_FIRST_HEADER_REGEX

    dataset_file = openFile(dataset_path)

    current_email = Email()
    dataset_matrix = []

    for line in dataset_file:

        # Check for a new email first header
        if getMatching(EMAIL_FIRST_HEADER_REGEX, line):
            if not current_email.isEmpty():
                dataset_matrix.append( [*current_email.getEmailData(), is_benign] )
            current_email.reset()
            continue

        # If email has body, appends the new line to its content
        if current_email.hasBody():
            current_email.body += line
            continue

        # If email has no subject, check if the line read is the subject
        if current_email.hasNoSubject():
            subject_match = getMatching(EMAIL_SUBJECT_REGEX, line)
            if subject_match:
                current_email.subject = subject_match
                continue

        # If email has no content type, check if the line read is the content type
        if current_email.hasNoContentType():
            content_type_match = getMatching(EMAIL_CONTENT_TYPE_REGEX, line)
            if content_type_match:
                current_email.content_type = content_type_match
                continue

        # Check if the line read is the start of the email's body
        body_start_match = getMatching(EMAIL_BODY_START_REGEX, line)
        if body_start_match:
            current_email.body = ''


    dataset_file.close()
    return dataset_matrix


if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)
    stdout = sys.stdout

    if argc != 2:
        stdout.write('Usage: python3 read-dataset.py <dataset>.txt\n')
        exit(1)

    dataset_path = argv[1]

    # Sets first header regex based on dataset type
    is_dataset_benign = 1 if dataset_path.find('benign') != -1 else 0
    dataset_matrix = readDataset(dataset_path, is_dataset_benign)

    stdout.write('Numero de emails = {}\n\n'.format(len(dataset_matrix)))
    try:
        os.mkdir('matrices')
    except:
        None
    open(f'./matrices/{"benign" if is_dataset_benign else "fraud"}_matrix.txt', 'w').write(f'{dataset_matrix}')
