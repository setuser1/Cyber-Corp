#include <SDL2/SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <math.h>

// ================= Base life struct =================
typedef struct {
    int age;
    char energy_state; // 'L', 'M', 'H'
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
    int x, y; // position
} plant;

// ================= Animal struct =================
typedef struct {
    life base;
    int raycasts; // radius
    float predation_rate; // 0 = herbivore, >0 = predator
    float hunger_rate;
    float size_modifier;
    float health;
    float strength;
    int species_id;
    int x, y; // position
    bool can_eat_decomposers;
} animal;

// ================= Decomposer struct =================
typedef struct {
    int x, y;
    float health;
    bool active;
} decomposer;

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
    // Slightly offset position
    offspring.x = parent->x + (rand()%11 - 5);
    offspring.y = parent->y + (rand()%11 - 5);
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
    offspring.x = parent->x + (rand()%11 - 5);
    offspring.y = parent->y + (rand()%11 - 5);
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
    if ((rand() / (float)RAND_MAX) > survival_prob || a->health <= 0) {
        a->base.deceased = true;
    }
}

// ================= SDL draw helpers =================
void draw_plant(SDL_Renderer *renderer, plant *p) {
    if (p->base.deceased) return;
    SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255); // green
    SDL_Rect rect = {p->x, p->y, 4, 4};
    SDL_RenderFillRect(renderer, &rect);
}

void draw_animal(SDL_Renderer *renderer, animal *a) {
    if (a->base.deceased) return;
    if (a->predation_rate > 0.1f) {
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); // predator red
    } else if (a->can_eat_decomposers) {
        SDL_SetRenderDrawColor(renderer, 128, 255, 0, 255); // special herbivore greenish
    } else {
        SDL_SetRenderDrawColor(renderer, 255, 255, 0, 255); // herbivore yellow
    }
    SDL_Rect rect = {a->x, a->y, 4, 4};
    SDL_RenderFillRect(renderer, &rect);
}

void draw_decomposer(SDL_Renderer *renderer, decomposer *d) {
    if (!d->active) return;
    SDL_SetRenderDrawColor(renderer, 128,128,128,255); // gray
    SDL_Rect rect = {d->x, d->y, 3,3};
    SDL_RenderFillRect(renderer, &rect);
}

// ================= Raycast eating =================
bool distance(int x1,int y1,int x2,int y2){
    return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)) <= 10; // radius 10
}

void animal_feed(animal *a, plant *plants, int plant_count, animal *animals, int animal_count, decomposer *decomposers, int dec_count) {
    if (a->base.deceased) return;
    bool must_eat = (a->base.energy_state == 'L') || (a->base.energy_state == 'M' && (rand()%2));
    if (!must_eat) return;

    // Herbivores eat plants
    if (a->predation_rate < 0.1f) {
        for (int i=0;i<plant_count;i++){
            if (!plants[i].base.deceased && distance(a->x,a->y,plants[i].x,plants[i].y)){
                a->health += 50;
                plants[i].base.deceased = true;
                break;
            }
        }
        // Can also eat decomposers if allowed
        if (a->can_eat_decomposers){
            for (int i=0;i<dec_count;i++){
                if (decomposers[i].active && distance(a->x,a->y,decomposers[i].x,decomposers[i].y)){
                    a->health += 30;
                    decomposers[i].active=false;
                    break;
                }
            }
        }
    } else { // Predator eats herbivore
        for (int i=0;i<animal_count;i++){
            if (!animals[i].base.deceased && animals[i].predation_rate < 0.1f && distance(a->x,a->y,animals[i].x,animals[i].y)){
                a->health += animals[i].health;
                animals[i].base.deceased=true;
                break;
            }
        }
    }
}

// Decomposers eat dead plants or animals
void decomposer_feed(decomposer *d, plant *plants, int plant_count, animal *animals, int animal_count){
    if (!d->active) return;
    for (int i=0;i<plant_count;i++){
        if (plants[i].base.deceased && distance(d->x,d->y,plants[i].x,plants[i].y)){
            d->health += 20;
            plants[i].base.deceased = false; // eaten
            break;
        }
    }
    for (int i=0;i<animal_count;i++){
        if (animals[i].base.deceased && distance(d->x,d->y,animals[i].x,animals[i].y)){
            d->health += 20;
            animals[i].base.deceased = false; // eaten
            break;
        }
    }
}

// ================= Main =================
int main(){
    srand(time(NULL));
    const int plant_capacity=50;
    const int animal_capacity=30;
    const int decomposer_capacity=20;

    plant *plants=malloc(sizeof(plant)*plant_capacity);
    animal *animals=malloc(sizeof(animal)*animal_capacity);
    decomposer *decomposers=malloc(sizeof(decomposer)*decomposer_capacity);

    // Init plants
    for (int i=0;i<plant_capacity;i++){
        plants[i].base.age=0;
        plants[i].base.deceased=false;
        plants[i].base.mutation_rate=0.01f;
        plants[i].width=2.0f + ((rand()%10)/10.0f);
        plants[i].photosynthesis_rate=1.0f+((rand()%10)/10.0f);
        plants[i].health=500.0f;
        plants[i].drops_fruit=true;
        plants[i].species_id=1;
        plants[i].x=rand()%800;
        plants[i].y=rand()%600;
    }

    // Init animals
    for (int i=0;i<animal_capacity;i++){
        animals[i].base.age=0;
        animals[i].base.deceased=false;
        animals[i].base.mutation_rate=0.02f;
        animals[i].strength=10.0f+rand()%10;
        animals[i].size_modifier=1.0f+(rand()%5)/10.0f;
        animals[i].health=50.0f+rand()%20;
        animals[i].hunger_rate=0.5f;
        animals[i].predation_rate=(i%2==0)?0.6f:0.0f;
        animals[i].species_id=1;
        animals[i].x=rand()%800;
        animals[i].y=rand()%600;
        animals[i].can_eat_decomposers=(i%5==0);
        animals[i].base.energy_state='M';
    }

    // Init decomposers
    for (int i=0;i<decomposer_capacity;i++){
        decomposers[i].x=rand()%800;
        decomposers[i].y=rand()%600;
        decomposers[i].health=30;
        decomposers[i].active=false;
    }

    if(SDL_Init(SDL_INIT_VIDEO)!=0){
        printf("SDL Init Error: %s\n",SDL_GetError());
        return 1;
    }

    SDL_Window *win=SDL_CreateWindow("Ecosystem",100,100,800,600,SDL_WINDOW_SHOWN);
    SDL_Renderer *renderer=SDL_CreateRenderer(win,-1,SDL_RENDERER_ACCELERATED);

    const int timesteps=10000;
    const int target_fps=60;
    const int frame_delay=1000/target_fps;

    for(int t=0;t<timesteps;t++){
        Uint32 frame_start=SDL_GetTicks();

        SDL_SetRenderDrawColor(renderer,0,0,0,255);
        SDL_RenderClear(renderer);

        // Update plants
        for(int i=0;i<plant_capacity;i++){
            if(!plants[i].base.deceased){
                plants[i].health += plants[i].photosynthesis_rate*0.1f;
                survival_check_plant(&plants[i]);
                draw_plant(renderer,&plants[i]);
                if((rand()/(float)RAND_MAX)<0.001f) plants[i].species_id+=1;
            }
        }

        // Update animals
        for(int i=0;i<animal_capacity;i++){
            if(!animals[i].base.deceased){
                animals[i].health -= animals[i].hunger_rate;
                // Update energy state
                if(animals[i].health<30) animals[i].base.energy_state='L';
                else if(animals[i].health<60) animals[i].base.energy_state='M';
                else animals[i].base.energy_state='H';

                animal_feed(&animals[i],plants,plant_capacity,animals,animal_capacity,decomposers,decomposer_capacity);
                survival_check_animal(&animals[i]);
                draw_animal(renderer,&animals[i]);
                if((rand()/(float)RAND_MAX)<0.001f) animals[i].species_id+=1;
            }
        }

        // Update decomposers
        for(int i=0;i<decomposer_capacity;i++){
            if(!decomposers[i].active){
                // Spawn near dead entity
                for(int j=0;j<plant_capacity;j++){
                    if(plants[j].base.deceased){decomposers[i].x=plants[j].x; decomposers[i].y=plants[j].y; decomposers[i].active=true; break;}
                }
                for(int j=0;j<animal_capacity;j++){
                    if(animals[j].base.deceased){decomposers[i].x=animals[j].x; decomposers[i].y=animals[j].y; decomposers[i].active=true; break;}
                }
            }
            if(decomposers[i].active){
                decomposer_feed(&decomposers[i],plants,plant_capacity,animals,animal_capacity);
                draw_decomposer(renderer,&decomposers[i]);
                if(decomposers[i].health<=0) decomposers[i].active=false;
            }
        }

        SDL_RenderPresent(renderer);

        Uint32 frame_time=SDL_GetTicks()-frame_start;
        if(frame_delay>frame_time) SDL_Delay(frame_delay-frame_time);

        SDL_Event e;
        while(SDL_PollEvent(&e)){
            if(e.type==SDL_QUIT) t=timesteps;
        }
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(win);
    SDL_Quit();

    free(plants);
    free(animals);
    free(decomposers);

    return 0;
}
