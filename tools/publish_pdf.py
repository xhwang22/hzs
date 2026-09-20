"""Publish Tectonic output in place while preserving its PDF.js document identity.

Only the first trailer /ID changes; the new version ID and all content stay intact.
This deliberately supports Tectonic's unencrypted, non-incremental XRef-stream PDFs,
not arbitrary PDF rewriting. No third-party Python packages are required.
"""
import argparse
import os
from pathlib import Path
import re


def trailer_id(pdf):
    """Return the fixed-width first-ID match in the final XRef dictionary."""
    if not pdf.startswith(b'%PDF-'):
        raise ValueError('Input is not a PDF')
    ending = re.search(rb'startxref\s+(\d+)\s+%%EOF\s*\Z', pdf)
    if not ending:
        raise ValueError('PDF has no complete end-of-file trailer')
    start = int(ending.group(1))
    stream = pdf.find(b'stream', start, ending.start())
    header = pdf[start:stream]
    if (stream < 0 or not re.match(rb'\d+\s+\d+\s+obj\s*<<', header)
            or not re.search(rb'/Type\s*/XRef\b', header)):
        raise ValueError('Expected a Tectonic XRef-stream PDF')
    if re.search(rb'/(?:Encrypt|Prev)\b', header):
        raise ValueError('Encrypted or incremental PDFs are not supported')
    pattern = re.compile(rb'/ID\s*\[\s*<([0-9a-fA-F]{32})>\s*<([0-9a-fA-F]{32})>\s*\]')
    matches = list(pattern.finditer(pdf, start, stream))
    if len(matches) != 1:
        raise ValueError('Expected exactly one pair of 16-byte hexadecimal PDF IDs')
    if int(matches[0].group(1), 16) == 0:
        raise ValueError('PDF document ID must not be zero')
    return matches[0]


def preserve_identity(compiled, previous=None):
    current_id = trailer_id(compiled)
    if previous is None:
        return compiled
    stable_id = trailer_id(previous).group(1)
    start, end = current_id.span(1)
    # Equal-length replacement leaves every cross-reference offset unchanged.
    return compiled[:start] + stable_id + compiled[end:]


def publish(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Compile and publish paths must be different')
    compiled = source.read_bytes()
    previous = destination.read_bytes() if destination.exists() else None
    result = preserve_identity(compiled, previous)
    # Validate before opening the destination; preserve its inode for file watchers.
    with destination.open('r+b' if previous is not None else 'xb') as output:
        output.write(result)
        output.truncate()
        output.flush()
        os.fsync(output.fileno())
    os.utime(destination, None)
    match = trailer_id(result)
    print('Published {} (document ID {}; version ID {})'.format(
        destination, match.group(1).decode(), match.group(2).decode()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        publish(args.source, args.destination)
    except (OSError, ValueError) as error:
        parser.exit(1, 'PDF publication failed: {}\n'.format(error))


if __name__ == '__main__':
    main()
