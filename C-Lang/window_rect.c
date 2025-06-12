#include <SDL2/SDL.h>
#include <stdio.h>
#include <math.h>

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

// Draw a filled circle at (cx, cy) with radius r and color
void draw_filled_circle(SDL_Renderer *renderer, int cx, int cy, int r, Uint8 rcol, Uint8 gcol, Uint8 bcol, Uint8 acol) {
    SDL_SetRenderDrawColor(renderer, rcol, gcol, bcol, acol);
    for (int y = -r; y <= r; y++) {
        for (int x = -r; x <= r; x++) {
            if (x * x + y * y <= r * r) {
                SDL_RenderDrawPoint(renderer, cx + x, cy + y);
            }
        }
    }
}

void run_rotating_texture(SDL_Renderer *renderer, SDL_Texture *texture, SDL_Rect dest_rect) {
    int running = 1;
    int angle = 0;
    SDL_Event event;
    int win_w = 800, win_h = 600;

    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT)
                running = 0;
            else if (event.type == SDL_WINDOWEVENT && event.window.event == SDL_WINDOWEVENT_SIZE_CHANGED) {
                win_w = event.window.data1;
                win_h = event.window.data2;
            } else if (event.type == SDL_KEYDOWN) {
                switch (event.key.keysym.sym) {
                    case SDLK_w: angle = (angle - 5) % 360; break;
                    case SDLK_s: angle = (angle + 2) % 360; break;
                    case SDLK_a: angle = (angle - 5) % 360; break;
                    case SDLK_d: angle = (angle + 2) % 360; break;
                    case SDLK_ESCAPE: running = 0; break;
                }
            }
        }
        angle = (angle + 1) % 360;
        SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255);
        SDL_RenderClear(renderer);

        // Draw the rotating rectangle texture
        SDL_RenderCopyEx(renderer, texture, NULL, &dest_rect, angle, NULL, SDL_FLIP_NONE);

        // Draw a large dark circle (outer)
        int circle_cx = dest_rect.x + dest_rect.w / 2;
        int circle_cy = dest_rect.y + dest_rect.h / 2;
        int outer_r = 60;
        int inner_r = 30;
        draw_filled_circle(renderer, circle_cx, circle_cy, outer_r, 200, 200, 200, 255);   // dark red

        // Get mouse position
        int mouse_x, mouse_y;
        SDL_GetMouseState(&mouse_x, &mouse_y);

        // Calculate angle from center to mouse
        float dx = mouse_x - circle_cx;
        float dy = mouse_y - circle_cy;
        float face_angle = atan2f(dy, dx);

        // Inner circle center offset to "face" the mouse
        int face_offset = 20;
        int inner_cx = circle_cx + (int)(cosf(face_angle) * face_offset);
        int inner_cy = circle_cy + (int)(sinf(face_angle) * face_offset);

        // Draw a smaller, even darker circle inside, offset toward mouse
        draw_filled_circle(renderer, inner_cx, inner_cy, inner_r, 10, 10, 10, 255);   // darker red

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

    run_rotating_texture(renderer, rect_texture, dest_rect);

    SDL_DestroyTexture(rect_texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
