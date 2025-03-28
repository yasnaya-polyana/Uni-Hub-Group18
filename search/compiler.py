"""Test for search string parsing."""

from dataclasses import dataclass


class Token:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"


class IntToken(Token):
    pass


class WhitespaceToken(Token):
    pass


class EqualsToken(Token):
    pass


class SoftStrToken(Token):
    pass


class HardStrToken(Token):
    pass


class EndToken(Token):
    pass


class VariableToken(Token):
    def __init__(self, identifier: str, comparator: str, value_token: Token):
        self.identifier = identifier
        self.comparator = comparator
        self.value_token = value_token

    def __str__(self):
        return f"{self.__class__.__name__}({self.identifier}{self.comparator}{self.value_token})"


class Stage1Tokeniser:
    """Tokenise and parse search string."""

    def __init__(self, inp: str):
        self.inp = inp
        self.ptr = 0
        self.tokens = []

    def next(self):
        """Get next char in input."""
        self.ptr += 1
        if self.ptr > len(self.inp):
            return "\0"
        return self.inp[self.ptr - 1]

    def peek(self):
        if self.ptr > len(self.inp) - 1:
            return "\0"
        return self.inp[self.ptr]

    def run(self):
        """Tokenise stage 1."""
        char = self.peek()
        while char != "\0":
            if char.isdigit():
                self.tokenise_int()
            elif char == " ":
                self.tokens.append(WhitespaceToken(self.next()))
            elif char in "=<>":
                self.tokens.append(EqualsToken(self.next()))
            elif char.isalpha():
                self.tokenise_soft_str()
            elif char in ("'", '"'):
                self.tokenise_hard_str()
            else:
                print("UNMATCHED ", self.next())

            char = self.peek()

        self.tokens.append(EndToken("\0"))

    def tokenise_int(self):
        int_str = ""
        while self.peek().isdigit():
            int_str += self.next()

        self.tokens.append(IntToken(int_str))

    def tokenise_soft_str(self):
        string = ""
        while self.peek().isalpha() or self.peek() in "-;":
            string += self.next()

        self.tokens.append(SoftStrToken(string))

    def tokenise_hard_str(self):
        terminators = ("\0", self.next())
        string = ""
        while self.peek() not in terminators:
            string += self.next()

        self.next()
        self.tokens.append(HardStrToken(string))


class Stage2Tokeniser:
    """Tokenise and parse search tokens."""

    def __init__(self, inp: list[Token]):
        self.inp = inp
        self.ptr = 0
        self.tokens = []

    def next(self):
        """Get next token in input."""
        self.ptr += 1
        if self.ptr > len(self.inp):
            return EndToken("\0")
        return self.inp[self.ptr - 1]

    def peek(self, ahead_by: int = 0):
        if self.ptr > len(self.inp) - 1:
            return EndToken("\0")
        return self.inp[self.ptr + ahead_by]

    def run(self):
        """Tokenise stage 1."""
        token = self.peek()
        while not isinstance(token, EndToken):
            if isinstance(token, SoftStrToken) and isinstance(
                self.peek(1), EqualsToken
            ):
                self.tokenise_variable()
            else:
                self.tokens.append(self.next())

            token = self.peek()

        self.tokens.append(EndToken("\0"))

    def tokenise_variable(self):
        self.tokens.append(
            VariableToken(self.next().value, self.next().value, self.next())
        )


@dataclass
class SearchQuery:
    """Used to execute search."""

    search_str: str
    conditions: dict

    def __str__(self):
        return self.search_str + " " + str(self.conditions)


class Parser:
    """Parse search tokens."""

    def __init__(self, inp: list[Token], search_query: SearchQuery):
        self.inp = inp
        self.ptr = 0
        self.result = search_query

    def next(self):
        """Get next token in input."""
        self.ptr += 1
        if self.ptr > len(self.inp):
            return EndToken("\0")
        return self.inp[self.ptr - 1]

    def peek(self, ahead_by: int = 0):
        if self.ptr > len(self.inp) - 1:
            return EndToken("\0")
        return self.inp[self.ptr + ahead_by]

    def run(self):
        """Tokenise stage 1."""
        token = self.peek()
        while not isinstance(token, EndToken):
            if isinstance(token, VariableToken):
                self.parse_variable()
            elif isinstance(
                token, (WhitespaceToken, IntToken, SoftStrToken, HardStrToken)
            ):
                self.result.search_str += self.next().value
            else:
                print("UNHANDLED ", self.next())

            token = self.peek()

        self.clean_up()

    def clean_up(self):
        self.result.search_str = self.result.search_str.strip()

    def parse_variable(self):
        token: VariableToken = self.next()
        print("TOKEN", token)
        self.result.conditions[token.identifier] = (token.comparator, token.value_token)


class SearchCompiler:
    def __init__(self, search_str: str):
        self.search_str = search_str

    def compile(self) -> SearchQuery:
        search_query = SearchQuery("", {})
        tokeniser = Stage1Tokeniser(self.search_str)
        tokeniser.run()

        tokeniser2 = Stage2Tokeniser(tokeniser.tokens)
        tokeniser2.run()

        parser = Parser(tokeniser2.tokens, search_query)
        parser.run()

        print(search_query)
        return search_query
