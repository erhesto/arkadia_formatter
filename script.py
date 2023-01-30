import os
import random
import itertools


class Formatter:
    def __init__(
        self, 
        left_margin_size=2, 
        right_margin_size=2, 
        width=80, 
        border='|', 
        indent=2,
        rjust=True
    ):
        self.left_margin_size = left_margin_size
        self.right_margin_size = right_margin_size
        self.width = width
        self.border = border
        self.indent = indent * ' '
        self.rjust = rjust

    @property
    def left_margin(self):
        return ' ' * self.left_margin_size

    @property
    def right_margin(self):
        return ' ' * self.right_margin_size

    @property
    def inner_width(self):
        return self.width - self.borders_size - self.margins

    @property
    def borders_size(self):
        return 2 * len(self.border)

    @property
    def margins(self):
        return self.left_margin_size + self.right_margin_size

    def make_line(self, line, last_line=False):
        text_length = len(''.join(line))
        spaces = (len(line) - 1) * [" "]

        if not self.rjust or not spaces or last_line:
            return ' '.join(line).ljust(self.inner_width)
    
        counter = len(line) - 1
        while counter + text_length < self.inner_width:
            spaces[random.randrange(0, len(spaces))] += " "
            counter += 1

        return "".join(
            itertools.chain.from_iterable(itertools.zip_longest(line, spaces, fillvalue=""))
        )

    def make_output_line(self, line):
        return (
            f'{self.border}'
            f'{self.left_margin}'
            f'{line}'
            f'{self.right_margin}'
            f'{self.border}'
        )




class Letter:
    def __init__(self, raw_letter, formatter):
        maker = SectionMaker(formatter)
        self._formatter = formatter
        self._sections = list(map(maker, raw_letter.split('\n')))

    def horizontal_line(self):
        return ['-' * self._formatter.width]

    def __str__(self):
        head = self.horizontal_line()
        body = list(str(section) for section in self._sections)
        bottom = self.horizontal_line()
        
        all_lines = head + body + bottom
        return '\n'.join(all_lines)




class SectionMaker:
    def __init__(self, formatter):
        self._formatter = formatter

    def __call__(self, line):
        section_type = Section

        if line.startswith('$'):
            section_type = Dialogue
        elif line.startswith('***'):
            section_type = ChapterBreak
        elif not line:
            section_type = EmptyLine

        return section_type(line, self._formatter)


class Section:
    def __init__(self, raw_line, formatter):
        self._raw_line = raw_line.strip()
        self._formatter = formatter

    def __bool__(self):
        return bool(self._raw_line)

    def __str__(self):
        return '\n'.join(map(self._formatter.make_output_line, self._lines))

    @property
    def _lines(self):
        words = self._raw_line.split()
        words = [self._formatter.indent + words[0]] + words[1:]
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_len = len(word) + 1
            if current_length + word_len <= self._formatter.inner_width:
                current_length += word_len
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
                current_length = word_len
        else:
            lines.append(current_line)

        whole_lines = [self._formatter.make_line(line) for line in lines[:-1]]
        whole_lines += [self._formatter.make_line(lines[-1], last_line=True)]
        return whole_lines


class ChapterBreak(Section):
    @property
    def _lines(self):
        return [
            self._raw_line.center(self._formatter.inner_width), 
        ]


class EmptyLine(Section):
    @property
    def _lines(self):
        return [' ' * self._formatter.inner_width]


class Dialogue(Section):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_line = self._raw_line.replace('$', '- ')





def main():
    filename = os.environ['FILENAME2READ']
    border = os.environ.get('BORDER', '')
    width = int(os.environ.get('WIDTH', 80))
    raw_letter = open(filename).read()
    formatter = Formatter(border=border, width=width)
    print(str(Letter(raw_letter, formatter)))


if __name__ == '__main__':
    main()
