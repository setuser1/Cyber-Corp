#include <SDL2/SDL.h>
#include <stdio.h>
#include <math.h>

SDL_Texture* create_red_rect_texture(SDL_Renderer *renderer) {
    SDL_Texture *texture = SDL_CreateTexture(
        renderer,
        SDL_PIXELFORMAT_RGBA8888,
        SDL_TEXTUREACCESS_TARGET,
        200, 150
    );
    SDL_SetRenderTarget(renderer, texture);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 0);
    SDL_RenderClear(renderer);
    SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
    SDL_Rect rect = {0, 0, 200, 150};
    SDL_RenderFillRect(renderer, &rect);
    SDL_SetRenderTarget(renderer, NULL);
    return texture;
}

void draw_circle(SDL_Renderer *renderer, int x, int y, int radius, SDL_Color color) {
    for (int w = 0; w < radius * 2; w++) {
        for (int h = 0; h < radius * 2; h++) {
            int dx = radius - w;
            int dy = radius - h;
            if ((dx * dx + dy * dy) <= (radius * radius)) {
                SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, color.a);
                SDL_RenderDrawPoint(renderer, x + dx, y + dy);
            }
        }
    }
}

void draw_tracking_eyes(SDL_Renderer *renderer) {
    int rect_x = 300;
    int rect_y = 225;
    int rect_w = 200;
    int rect_h = 150;

    int center_x = rect_x + rect_w / 2;
    int center_y = rect_y + rect_h / 2;

    int left_eye_x = center_x - 40;
    int left_eye_y = center_y;
    int right_eye_x = center_x + 40;
    int right_eye_y = center_y;

    int mouse_x, mouse_y;
    SDL_GetMouseState(&mouse_x, &mouse_y);

    float angle_left = atan2(mouse_y - left_eye_y, mouse_x - left_eye_x);
    float angle_right = atan2(mouse_y - right_eye_y, mouse_x - right_eye_x);

    int eye_radius = 20;
    int pupil_radius = 8;
    float pupil_offset = 4.0f;

    SDL_Color white = {255, 255, 255, 255};
    SDL_Color black = {0, 0, 0, 255};

    draw_circle(renderer, left_eye_x, left_eye_y, eye_radius, white);
    draw_circle(renderer, right_eye_x, right_eye_y, eye_radius, white);

    int pupil_left_x = (int)(left_eye_x + cos(angle_left) * pupil_offset);
    int pupil_left_y = (int)(left_eye_y + sin(angle_left) * pupil_offset);
    int pupil_right_x = (int)(right_eye_x + cos(angle_right) * pupil_offset);
    int pupil_right_y = (int)(right_eye_y + sin(angle_right) * pupil_offset);

    draw_circle(renderer, pupil_left_x, pupil_left_y, pupil_radius, black);
    draw_circle(renderer, pupil_right_x, pupil_right_y, pupil_radius, black);
}

void run(SDL_Renderer *renderer, SDL_Texture *texture) {
    int running = 1;
    SDL_Event event;
    while (running) {
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT ||
                (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE)) {
                running = 0;
            }
        }
        SDL_SetRenderDrawColor(renderer, 30, 30, 30, 255);
        SDL_RenderClear(renderer);

        SDL_Rect dest_rect = {300, 225, 200, 150};
        SDL_RenderCopy(renderer, texture, NULL, &dest_rect);
        draw_tracking_eyes(renderer);

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
    SDL_Texture *rect_texture = create_red_rect_texture(renderer);

    run(renderer, rect_texture);

    SDL_DestroyTexture(rect_texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
