#include <SDL2/SDL.h>
#include <stdio.h>

SDL_Texture* create_red_rect_texture(SDL_Renderer *renderer, int w, int h) {
    SDL_Texture *texture = SDL_CreateTexture(
        renderer,
        SDL_PIXELFORMAT_RGBA8888,
        SDL_TEXTUREACCESS_TARGET,
        w, h
    );
    SDL_SetRenderTarget(renderer, texture);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0);
    SDL_RenderClear(renderer);
    SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
    SDL_Rect rect = {0, 0, w, h};
    SDL_RenderFillRect(renderer, &rect);
    SDL_SetRenderTarget(renderer, NULL);
    return texture;
}


void run(SDL_Renderer *renderer, SDL_Texture *texture, SDL_Rect dest_rect) {
    int running = 1;
    int speed = 5; // pixels per frame
    SDL_Event event;
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT)
                running = 0;
            else if (event.type == SDL_KEYDOWN) {
                switch (event.key.keysym.sym) {
                    case SDLK_w: dest_rect.y -= speed; break;
                    case SDLK_s: dest_rect.y += speed; break;
                    case SDLK_a: dest_rect.x -= speed; break;
                    case SDLK_d: dest_rect.x += speed; break;
                    case SDLK_ESCAPE: running = 0; break;
                }
            }
        }
        SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255);
        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, NULL, &dest_rect);
        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }
}

void run_rotating_texture(SDL_Renderer *renderer, SDL_Texture *texture, SDL_Rect dest_rect) {
    int running = 1;
    int angle = 0;
    SDL_Event event;

    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT)
                running = 0;
            else if (event.type == SDL_KEYDOWN) {
                switch (event.key.keysym.sym) {
                    case SDLK_w: angle = (angle - 10) % 360; break;
                    case SDLK_s: angle += 5; break;
                    case SDLK_a: angle = (angle - 10) % 360; break;
                    case SDLK_d: angle += 5; break;
                    case SDLK_ESCAPE: running = 0; break;
                }
            }
        }
        angle = (angle + 1) % 360;
        SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255);
        SDL_RenderClear(renderer);
        SDL_RenderCopyEx(renderer, texture, NULL, &dest_rect, angle, NULL, SDL_FLIP_NONE);
        SDL_RenderPresent(renderer);
        SDL_Delay(16);
    }
}

int main() {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL_Init Error: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Window *window = SDL_CreateWindow(
        "It commands you.",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        800, 600,
        SDL_WINDOW_RESIZABLE
    );
    if (!window) {
        printf("SDL_CreateWindow Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    SDL_Renderer *renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture *rect_texture = create_red_rect_texture(renderer, 200, 150);
    SDL_Rect dest_rect = { 300, 225, 200, 150 };

    // run(renderer, rect_texture, dest_rect);
    run_rotating_texture(renderer, rect_texture, dest_rect);

    SDL_DestroyTexture(rect_texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
