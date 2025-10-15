//
// Created by tink on 10/15/25.
//

#ifndef C_TRIANGLE_COMPILER_H
#define C_TRIANGLE_COMPILER_H


// data structures
typedef enum {
    // ===== Arithmetic Operators =====
    TOK_PLUS, TOK_MINUS, TOK_STAR, TOK_SLASH, TOK_PERCENT,
    TOK_INCREMENT, TOK_DECREMENT,

    // ===== Assignment Operators =====
    TOK_ASSIGN, TOK_PLUS_ASSIGN, TOK_MINUS_ASSIGN, TOK_MUL_ASSIGN,
    TOK_DIV_ASSIGN, TOK_MOD_ASSIGN,

    // ===== Comparison Operators =====
    TOK_EQ, TOK_NEQ, TOK_LT, TOK_GT, TOK_LTE, TOK_GTE,

    // ===== Logical Operators =====
    TOK_AND, TOK_OR, TOK_NOT,

    // ===== Bitwise Operators =====
    TOK_BIT_AND, TOK_BIT_OR, TOK_BIT_XOR, TOK_BIT_NOT,
    TOK_LSHIFT, TOK_RSHIFT,

    // ===== Pointer / Address Operators =====
    TOK_AMPERSAND, TOK_STAR_DEREF, TOK_ARROW,

    // ===== Array / Indexing =====
    TOK_LBRACKET, TOK_RBRACKET,

    // ===== Parentheses / Braces =====
    TOK_LPAREN, TOK_RPAREN, TOK_LBRACE, TOK_RBRACE,

    // ===== Delimiters & Misc Symbols =====
    TOK_SEMICOLON, TOK_COLON, TOK_COMMA, TOK_DOT, TOK_QUESTION, TOK_HASH, TOK_HASHHASH,

    // ===== Type Keywords =====
    TOK_VOID, TOK_CHAR, TOK_SHORT, TOK_INT, TOK_LONG, TOK_LONG_LONG,
    TOK_FLOAT, TOK_DOUBLE, TOK_SIGNED, TOK_UNSIGNED, TOK_CONST, TOK_VOLATILE,
    TOK_STATIC, TOK_EXTERN, TOK_STRUCT, TOK_UNION, TOK_ENUM, TOK_TYPEDEF, TOK_SIZEOF,

    // ===== Control Keywords =====
    TOK_IF, TOK_ELSE, TOK_FOR, TOK_WHILE, TOK_DO, TOK_SWITCH, TOK_CASE,
    TOK_DEFAULT, TOK_BREAK, TOK_CONTINUE, TOK_RETURN, TOK_GOTO,

    // ===== Literals & Identifiers =====
    TOK_IDENTIFIER, TOK_INT_LITERAL, TOK_FLOAT_LITERAL,
    TOK_DOUBLE_LITERAL, TOK_CHAR_LITERAL, TOK_STRING_LITERAL,

    TOK_UNKNOWN,
    TOK_EOF
} TokenType;


typedef struct {
    TokenType type;
    char *text; // malloc'd string
} Token;

typedef struct {
    const char *src;
    Token lookahead;
} Lexer;

typedef enum {
    TYPE_FUNC,
    TYPE_VAR,
    TYPE_DEF,
    TYPE_BLOCK,
    TYPE_CALL,
    TYPE_PROGRAM,
} point;

typedef struct {
    char *name;
    point type;
} pointer;

typedef struct {
    pointer base;
    pointer* node;
} line;

typedef struct {
    point type:TYPE_PROGRAM;
    pointer* variables;
    pointer* functions;
} program;


// lexer functions
char* read_file(const char *filename);
TokenType check_keyword(const char *text);
Token lex_token(Lexer *lexer);
Token lexer_peek(Lexer *lexer);
Token lexer_next(Lexer *lexer);

// parser functions



#endif //C_TRIANGLE_COMPILER_H