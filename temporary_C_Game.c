#include <SDL3/SDL.h>
#include <SDL3/SDL_video.h>
#include <stdio.h>

typedef struct {
    struct {
        float x, y;
        float vx, vy;
        bool death;
        bool on_ground;
    } Player;

    SDL_Renderer* Renderer;
    SDL_Event Event;
    SDL_Window* Window;
    int Width, Height;
    char* Title;
    bool Running;

} Program;




Program init(Program *program) {
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        fprintf(stderr, "SDL_Init failed: %s\n", SDL_GetError());
    }

    program->Window = SDL_CreateWindow(program->Title,
                                       program->Width,
                                       program->Height,
                                       0
                                       );
    if (!program->Window) {
        fprintf(stderr, "SDL_CreateWindow failed: %s\n", SDL_GetError());
    }

    program->Renderer = SDL_CreateRenderer(program->Window, nullptr);
    if (!program->Renderer) {
        fprintf(stderr, "SDL_CreateRenderer failed: %s\n", SDL_GetError());
    }

    return *program;
}

void cleanup(const Program *program) {
    SDL_DestroyRenderer(program->Renderer);
    SDL_DestroyWindow(program->Window);
    SDL_Quit();
}


void setup_player(Program *program, const float start_x, const float start_y, const int player_size, const int window_height) {
    const int ground_level = window_height - player_size;
    
    program->Player.x = start_x;
    program->Player.y = (float)ground_level - start_y;
    program->Player.vx = 0;
    program->Player.vy = 0;
    program->Player.on_ground = false;
    program->Running = true;
}

void apply_physics(Program *program, const float gravity) {

    if (!program->Player.on_ground) {
        program->Player.vy += gravity;
    }

    program->Player.x += program->Player.vx;
    program->Player.y += program->Player.vy;
}

void check_collisions(Program *program, const int player_size, const int window_width, const int window_height) {
    const int ground_level = window_height - player_size;

    if (program->Player.x < 0) {
        program->Player.x = 0;
        program->Player.vx = 0;
    }
    if (program->Player.x + (float)player_size > (float)window_width) {
        program->Player.x = (float)window_width - (float)player_size;
        program->Player.vx = 0;
    }

    if (program->Player.y + (float)player_size >= (float)ground_level) {
        program->Player.y = (float)ground_level - (float)player_size;
        program->Player.vy = 0;
        program->Player.on_ground = true;
    } else {
        program->Player.on_ground = false;
    }

    if (program->Player.y < 0) {
        program->Player.y = 0;
        program->Player.vy = 0;
    }
}

void handle_input(Program *program, float move_speed, float jump_strength) {
    const bool *keys = SDL_GetKeyboardState(NULL);

    program->Player.vx = 0;
    if (keys[SDL_SCANCODE_A]) {
        program->Player.vx = -move_speed;
    }
    if (keys[SDL_SCANCODE_D]) {
        program->Player.vx = move_speed;
    }

    if (keys[SDL_SCANCODE_W] && program->Player.on_ground) {
        program->Player.vy = jump_strength;
        program->Player.on_ground = false;
    }
}

void mainloop(Program *program, float gravity, float move_speed, float jump_strength, int player_size, float start_x, float start_y) {
    const int ground_level = program->Height - player_size;

    setup_player(program, start_x, start_y, player_size, program->Height);

    while (program->Running) {
        while (SDL_PollEvent(&program->Event)) {
            if (program->Event.type == SDL_EVENT_QUIT) {
                program->Running = false;
            }
        }

        handle_input(program, move_speed, jump_strength);


        apply_physics(program, gravity);
        check_collisions(program, player_size, program->Width, program->Height);

        // Draw
        SDL_SetRenderDrawColor(program->Renderer, 0, 0, 0, 255);
        SDL_RenderClear(program->Renderer);

        SDL_SetRenderDrawColor(program->Renderer, 0, 255, 0, 255);
        SDL_FRect ground = {0, (float)ground_level, (float)program->Width, (float)player_size};
        SDL_RenderFillRect(program->Renderer, &ground);

        SDL_FRect player = {program->Player.x, program->Player.y, (float)player_size, (float)player_size};
        SDL_SetRenderDrawColor(program->Renderer, 255, 0, 0, 255);
        SDL_RenderFillRect(program->Renderer, &player);

        SDL_RenderPresent(program->Renderer);
        SDL_Delay(16);
    }
}



int main() {

    const float gravity = 0.65f;
    const float move_speed = 5.0f;
    const float jump_strength = -17.0f;
    const int player_size = 75;
    const float start_x = 200.0f;
    const float start_y = 200.0f;
    
    Program cool_game;
    cool_game.Title = "Cool Game";
    cool_game.Width = 1600;
    cool_game.Height = 1000;
    cool_game.Running = false;
    cool_game = init(&cool_game);
    mainloop(&cool_game, gravity, move_speed, jump_strength, player_size, start_x, start_y);
    cleanup(&cool_game);
}
