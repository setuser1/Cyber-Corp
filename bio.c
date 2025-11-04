#include <SDL2/SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

// ================= Base life struct =================
typedef struct {
    int age;
    char energy_state;
    int growth_rate;
    float reproduction_rate;
    bool reproducing;
    bool deceased;
    float mutation_rate;
} life;

// ================= Plant struct =================
typedef struct {
    life base;
    float width;
    float photosynthesis_rate;
    bool drops_fruit;
    float health;
    int species_id;
} plant;

// ================= Animal struct =================
typedef struct {
    life base;
    int raycasts;
    float predation_rate;
    float hunger_rate;
    float size_modifier;
    float health;
    float strength;
    int species_id;
} animal;

// ================= Mutation function =================
float mutate_trait(float trait, float mutation_rate) {
    float change = ((rand() / (float)RAND_MAX) * 2.0f - 1.0f) * mutation_rate;
    return trait + change;
}

// ================= Plant reproduction =================
plant reproduce_plant(plant *parent, int new_species_id) {
    plant offspring = *parent;
    offspring.base.age = 0;
    offspring.base.deceased = false;
    offspring.health = 500.0f;
    offspring.width = mutate_trait(parent->width, parent->base.mutation_rate);
    offspring.photosynthesis_rate = mutate_trait(parent->photosynthesis_rate, parent->base.mutation_rate);
    offspring.base.growth_rate = (int)mutate_trait(parent->base.growth_rate, parent->base.mutation_rate);
    offspring.base.reproduction_rate = mutate_trait(parent->base.reproduction_rate, parent->base.mutation_rate);
    offspring.species_id = new_species_id;
    return offspring;
}

// ================= Animal reproduction =================
animal reproduce_animal(animal *parent, int new_species_id) {
    animal offspring = *parent;
    offspring.base.age = 0;
    offspring.base.deceased = false;
    offspring.health = parent->health;
    offspring.size_modifier = mutate_trait(parent->size_modifier, parent->base.mutation_rate);
    offspring.strength = mutate_trait(parent->strength, parent->base.mutation_rate);
    offspring.hunger_rate = mutate_trait(parent->hunger_rate, parent->base.mutation_rate);
    offspring.base.growth_rate = (int)mutate_trait(parent->base.growth_rate, parent->base.mutation_rate);
    offspring.base.reproduction_rate = mutate_trait(parent->base.reproduction_rate, parent->base.mutation_rate);
    offspring.species_id = new_species_id;
    return offspring;
}

// ================= Fitness functions =================
float plant_fitness(plant *p) {
    if (p->base.deceased) return 0.0f;
    return p->health * p->photosynthesis_rate * p->width;
}

float animal_fitness(animal *a) {
    if (a->base.deceased) return 0.0f;
    return a->strength * a->size_modifier * a->health / (a->hunger_rate + 1.0f);
}

// ================= Survival check =================
void survival_check_plant(plant *p) {
    float fitness = plant_fitness(p);
    float survival_prob = fitness / 1000.0f;
    if ((rand() / (float)RAND_MAX) > survival_prob) {
        p->base.deceased = true;
    }
}

void survival_check_animal(animal *a) {
    float fitness = animal_fitness(a);
    float survival_prob = fitness / 100.0f;
    if ((rand() / (float)RAND_MAX) > survival_prob) {
        a->base.deceased = true;
    }
}

// ================= SDL draw helpers =================
void draw_plant(SDL_Renderer *renderer, int x, int y, plant *p) {
    if (p->base.deceased) return;
    SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255); // green
    SDL_Rect rect = {x, y, 4, 4};
    SDL_RenderFillRect(renderer, &rect);
}

void draw_animal(SDL_Renderer *renderer, int x, int y, animal *a) {
    if (a->base.deceased) return;
    if (a->predation_rate > 0.1f) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); // predator red
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255); // herbivore yellow
    }
    SDL_Rect rect = {x, y, 4, 4};
    SDL_RenderFillRect(renderer, &rect);
}

int main() {
    srand((unsigned int)time(NULL));

    const int plant_capacity = 50;
    const int animal_capacity = 30;

    plant *plants = malloc(sizeof(plant) * plant_capacity);
    animal *animals = malloc(sizeof(animal) * animal_capacity);

    // Initialize plants and animals
    for (int i = 0; i < plant_capacity; i++) {
        plants[i].base.age = 0;
        plants[i].base.deceased = false;
        plants[i].base.mutation_rate = 0.01f;
        plants[i].width = 2.0f + ((rand() % 10) / 10.0f);
        plants[i].photosynthesis_rate = 1.0f + ((rand() % 10) / 10.0f);
        plants[i].health = 500.0f;
        plants[i].drops_fruit = true;
        plants[i].species_id = 1;
    }

    for (int i = 0; i < animal_capacity; i++) {
        animals[i].base.age = 0;
        animals[i].base.deceased = false;
        animals[i].base.mutation_rate = 0.02f;
        animals[i].strength = 10.0f + ((rand() % 10));
        animals[i].size_modifier = 1.0f + ((rand() % 5) / 10.0f);
        animals[i].health = 50.0f + ((rand() % 20));
        animals[i].hunger_rate = 0.5f;
        animals[i].predation_rate = (i % 2 == 0) ? 0.6f : 0.0f;
        animals[i].species_id = 1;
    }

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL Init Error: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Window *win = SDL_CreateWindow("Ecosystem Simulation", 100, 100, 800, 600, SDL_WINDOW_SHOWN);
    SDL_Renderer *renderer = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);

    const int timesteps = 10000;
    const int target_fps = 60;
    const int frame_delay = 1000 / target_fps;

    for (int t = 0; t < timesteps; t++) {
        Uint32 frame_start = SDL_GetTicks();

        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        // Update and draw plants
        for (int i = 0; i < plant_capacity; i++) {
            if (!plants[i].base.deceased) {
                plants[i].health += plants[i].photosynthesis_rate * 0.1f;
                survival_check_plant(&plants[i]);
                draw_plant(renderer, rand() % 800, rand() % 600, &plants[i]);

                // Speciation chance
                if ((rand() / (float)RAND_MAX) < 0.001f) {
                    plants[i].species_id += 1;
                }
            }
        }

        // Update and draw animals
        for (int i = 0; i < animal_capacity; i++) {
            if (!animals[i].base.deceased) {
                animals[i].health -= animals[i].hunger_rate;
                survival_check_animal(&animals[i]);
                draw_animal(renderer, rand() % 800, rand() % 600, &animals[i]);

                // Speciation chance
                if ((rand() / (float)RAND_MAX) < 0.001f) {
                    animals[i].species_id += 1;
                }
            }
        }

        SDL_RenderPresent(renderer);

        // Limit FPS to ~60
        Uint32 frame_time = SDL_GetTicks() - frame_start;
        if (frame_delay > frame_time) {
            SDL_Delay(frame_delay - frame_time);
        }

        // Event handling
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) {
                t = timesteps;
            }
        }
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(win);
    SDL_Quit();

    free(plants);
    free(animals);

    return 0;
}
