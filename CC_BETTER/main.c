#include <stdio.h>
#include <stdlib.h>
#include "compiler.h"

int main(const int argc, char *argv[]) {
    char *source = NULL;
    Token *tokens = NULL;
    size_t capacity = 0, token_count = 0;

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <source_file>\n", argv[0]);
        return 1;
    }

    source = read_file(argv[1]);
    if (!source) {
        fprintf(stderr, "Failed to read file: %s\n", argv[1]);
        return 1;
    }

    Lexer lexer = {source, {TOK_UNKNOWN, NULL}};
    capacity = 16;
    tokens = malloc(sizeof(Token) * capacity);
    if (!tokens) {
        fprintf(stderr, "Failed to allocate token array\n");
        free(source);
        return 1;
    }

    Token tok;
    while (1) {
        tok = lexer_next(&lexer);

        // EOF cleanup
        if (tok.type == TOK_EOF) {
            if (tok.text)
                free(tok.text);
            break;
        }

        // Expand token array dynamically
        if (token_count >= capacity) {
            capacity *= 2;
            Token *new_tokens = realloc(tokens, sizeof(Token) * capacity);
            if (!new_tokens) {
                fprintf(stderr, "Failed to resize token array\n");

                // Free all existing allocations
                for (size_t i = 0; i < token_count; i++)
                    free(tokens[i].text);
                free(tokens);
                free(source);
                free(tok.text);
                return 1;
            }
            tokens = new_tokens;
        }

        tokens[token_count++] = tok;
    }

    // ✅ Print tokens
    printf("Tokens:\n");
    for (size_t i = 0; i < token_count; i++)
        printf("%3d : '%s'\n", tokens[i].type, tokens[i].text ? tokens[i].text : "(null)");

    // ✅ Free all tokens’ text
    for (size_t i = 0; i < token_count; i++)
        free(tokens[i].text);

    // ✅ Free master allocations
    free(tokens);
    free(source);

    return 0;
}
