// U suck truly

// lexer.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "compiler.h"

char *read_file(const char *filename) {
    FILE *f = fopen(filename, "rb");
    if (!f) return NULL;

    fseek(f, 0, SEEK_END);
    const long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    char *buffer = malloc(size + 1);
    if (!buffer) {
        fclose(f);
        return NULL;
    }

    fread(buffer, 1, size, f);
    buffer[size] = '\0';
    fclose(f);
    return buffer;
}

// -------------------- Keyword Check --------------------
TokenType check_keyword(const char *text) {
    switch (text[0]) {
        case 'v':
            if (strcmp(text, "void") == 0) return TOK_VOID;
            if (strcmp(text, "volatile") == 0) return TOK_VOLATILE;
            break;
        case 'c':
            if (strcmp(text, "char") == 0) return TOK_CHAR;
            if (strcmp(text, "const") == 0) return TOK_CONST;
            if (strcmp(text, "continue") == 0) return TOK_CONTINUE;
            if (strcmp(text, "case") == 0) return TOK_CASE;
            break;
        case 's':
            if (strcmp(text, "short") == 0) return TOK_SHORT;
            if (strcmp(text, "signed") == 0) return TOK_SIGNED;
            if (strcmp(text, "static") == 0) return TOK_STATIC;
            if (strcmp(text, "struct") == 0) return TOK_STRUCT;
            if (strcmp(text, "switch") == 0) return TOK_SWITCH;
            if (strcmp(text, "sizeof") == 0) return TOK_SIZEOF;
            break;
        case 'i': if (strcmp(text, "int") == 0) return TOK_INT;
            break;
        case 'l': if (strcmp(text, "long") == 0) return TOK_LONG;
            break;
        case 'f':
            if (strcmp(text, "float") == 0) return TOK_FLOAT;
            if (strcmp(text, "for") == 0) return TOK_FOR;
            break;
        case 'd':
            if (strcmp(text, "double") == 0) return TOK_DOUBLE;
            if (strcmp(text, "do") == 0) return TOK_DO;
            if (strcmp(text, "default") == 0) return TOK_DEFAULT;
            break;
        case 'e':
            if (strcmp(text, "else") == 0) return TOK_ELSE;
            if (strcmp(text, "enum") == 0) return TOK_ENUM;
            if (strcmp(text, "extern") == 0) return TOK_EXTERN;
            break;
        case 'r': if (strcmp(text, "return") == 0) return TOK_RETURN;
            break;
        case 'w': if (strcmp(text, "while") == 0) return TOK_WHILE;
            break;
        case 'u':
            if (strcmp(text, "unsigned") == 0) return TOK_UNSIGNED;
            if (strcmp(text, "union") == 0) return TOK_UNION;
            break;
        case 't': if (strcmp(text, "typedef") == 0) return TOK_TYPEDEF;
            break;
        case 'g': if (strcmp(text, "goto") == 0) return TOK_GOTO;
            break;
    }
    return TOK_IDENTIFIER;
}

// -------------------- Lex Token --------------------
Token lex_token(Lexer *lexer) {
    const char *p = lexer->src;
    while (isspace(*p)) p++; // skip spaces including newlines

    // End of file
    if (*p == '\0') return (Token){TOK_EOF, NULL};

    // Skip single-line comments
    if (p[0] == '/' && p[1] == '/') {
        p += 2;
        while (*p && *p != '\n') p++;
        lexer->src = p;
        return lex_token(lexer); // recursively get next token
    }

    // Skip multi-line comments
    if (p[0] == '/' && p[1] == '*') {
        p += 2;
        while (*p && !(p[0] == '*' && p[1] == '/')) p++;
        if (*p) p += 2; // skip closing */
        lexer->src = p;
        return lex_token(lexer); // continue with next token
    }

    // String literal (supports multiline via \)
    if (*p == '"') {
        const char *start = p++;
        while (*p && (*p != '"' || *(p - 1) == '\\')) p++;
        if (*p == '"') p++;
        const size_t len = p - start;
        char *text = malloc(len + 1);
        memcpy(text, start, len);
        text[len] = '\0';
        lexer->src = p;
        return (Token){TOK_STRING_LITERAL, text};
    }

    // Identifier / keyword
    if (isalpha(*p) || *p == '_') {
        const char *start = p;
        while (isalnum(*p) || *p == '_') p++;
        const size_t len = p - start;
        char *text = malloc(len + 1);
        memcpy(text, start, len);
        text[len] = '\0';
        lexer->src = p;
        return (Token){check_keyword(text), text};
    }

    // Numeric literal
    if (isdigit(*p)) {
        const char *start = p;
        while (isdigit(*p) || *p == '.') p++;
        size_t len = p - start;
        char *text = malloc(len + 1);
        memcpy(text, start, len);
        text[len] = '\0';
        lexer->src = p;
        return (Token){TOK_INT_LITERAL, text};
    }

    // Multi-character operators
    if (p[0] == '+' && p[1] == '+') {
        lexer->src = p + 2;
        return (Token){TOK_INCREMENT, strdup("++")};
    }
    if (p[0] == '-' && p[1] == '-') {
        lexer->src = p + 2;
        return (Token){TOK_DECREMENT, strdup("--")};
    }
    if (p[0] == '+' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_PLUS_ASSIGN, strdup("+=")};
    }
    if (p[0] == '-' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_MINUS_ASSIGN, strdup("-=")};
    }
    if (p[0] == '*' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_MUL_ASSIGN, strdup("*=")};
    }
    if (p[0] == '/' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_DIV_ASSIGN, strdup("/=")};
    }
    if (p[0] == '%' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_MOD_ASSIGN, strdup("%=")};
    }
    if (p[0] == '=' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_EQ, strdup("==")};
    }
    if (p[0] == '!' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_NEQ, strdup("!=")};
    }
    if (p[0] == '<' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_LTE, strdup("<=")};
    }
    if (p[0] == '>' && p[1] == '=') {
        lexer->src = p + 2;
        return (Token){TOK_GTE, strdup(">=")};
    }
    if (p[0] == '&' && p[1] == '&') {
        lexer->src = p + 2;
        return (Token){TOK_AND, strdup("&&")};
    }
    if (p[0] == '|' && p[1] == '|') {
        lexer->src = p + 2;
        return (Token){TOK_OR, strdup("||")};
    }
    if (p[0] == '<' && p[1] == '<') {
        lexer->src = p + 2;
        return (Token){TOK_LSHIFT, strdup("<<")};
    }
    if (p[0] == '>' && p[1] == '>') {
        lexer->src = p + 2;
        return (Token){TOK_RSHIFT, strdup(">>")};
    }
    if (p[0] == '#' && p[1] == '#') {
        lexer->src = p + 2;
        return (Token){TOK_HASHHASH, strdup("##")};
    }
    if (p[0] == '-' && p[1] == '>') {
        lexer->src = p + 2;
        return (Token){TOK_ARROW, strdup("->")};
    }

    // Single-character operators
    const char c = *p++;
    lexer->src = p;
    char *text = malloc(2);
    text[0] = c;
    text[1] = '\0';
    switch (c) {
        case '+': return (Token){TOK_PLUS, text};
        case '-': return (Token){TOK_MINUS, text};
        case '*': return (Token){TOK_STAR, text};
        case '/': return (Token){TOK_SLASH, text};
        case '%': return (Token){TOK_PERCENT, text};
        case '=': return (Token){TOK_ASSIGN, text};
        case '&': return (Token){TOK_AMPERSAND, text};
        case '|': return (Token){TOK_BIT_OR, text};
        case '^': return (Token){TOK_BIT_XOR, text};
        case '~': return (Token){TOK_BIT_NOT, text};
        case '!': return (Token){TOK_NOT, text};
        case '(': return (Token){TOK_LPAREN, text};
        case ')': return (Token){TOK_RPAREN, text};
        case '{': return (Token){TOK_LBRACE, text};
        case '}': return (Token){TOK_RBRACE, text};
        case '[': return (Token){TOK_LBRACKET, text};
        case ']': return (Token){TOK_RBRACKET, text};
        case ';': return (Token){TOK_SEMICOLON, text};
        case ':': return (Token){TOK_COLON, text};
        case ',': return (Token){TOK_COMMA, text};
        case '.': return (Token){TOK_DOT, text};
        case '?': return (Token){TOK_QUESTION, text};
        case '#': return (Token){TOK_HASH, text};
        default: return (Token){TOK_UNKNOWN, text};
    }
}

// -------------------- Lookahead / Next --------------------
Token lexer_peek(Lexer *lexer) {
    if (lexer->lookahead.text) return lexer->lookahead;
    lexer->lookahead = lex_token(lexer);
    return lexer->lookahead;
}

Token lexer_next(Lexer *lexer) {
    if (lexer->lookahead.text) {
        Token t = lexer->lookahead;
        lexer->lookahead.text = NULL; // mark consumed
        return t;
    }
    return lex_token(lexer);
}


// Created by tink on 10/10/25.
// AKA setuser1 AKA tinktonk AKA yours truly, Sibastiao Silva
