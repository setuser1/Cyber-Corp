using System;
using System.Collections.Generic;
using System.Threading;

class Zombie
{
    public string Name { get; set; }
    public double Health { get; set; }
    public double MovementSpeed { get; set; } // Units per second
    public double AttackSpeed { get; set; } // Attacks per second
    public double DistanceTraveled { get; set; }

    public Zombie(string name, double health, double movementSpeed, double attackSpeed)
    {
        Name = name;
        Health = health;
        MovementSpeed = movementSpeed;
        AttackSpeed = attackSpeed;
        DistanceTraveled = 0;
    }

    public void Update(double deltaTime)
    {
        if (Health > 0)
        {
            DistanceTraveled += MovementSpeed * deltaTime;
            Console.WriteLine($"{Name} - Health: {Health:F0}, Distance Traveled: {DistanceTraveled:F1} units");
        }
        else
        {
            Console.WriteLine($"{Name} has been defeated!");
        }
    }

    public void TakeDamage(double damage)
    {
        Health -= damage;
        if (Health < 0) Health = 0;
        Console.WriteLine($"{Name} took {damage} damage. Remaining Health: {Health:F0}");
    }
}

class GameSimulation
{
    static void Main()
    {
        List<Zombie> zombies = new List<Zombie>
        {
            new Zombie("Conehead Zombie", 370, 1.0, 0.5),
            new Zombie("Buckethead Zombie", 1100, 1.0, 0.5)
        };

        double gameTime = 0;
        const double deltaTime = 1.0; // 1 second steps
        const double damagePerSecond = 20.0; // Simulated pea shooter damage

        Console.WriteLine("Simulation started. Zombies advancing...");

        while (gameTime < 20) // Run simulation for 20 seconds
        {
            Console.WriteLine($"\nTime: {gameTime} seconds");

            foreach (var zombie in zombies)
            {
                zombie.Update(deltaTime);
                zombie.TakeDamage(damagePerSecond * deltaTime); // Apply damage
            }

            Thread.Sleep(1000); // Simulate 1 second delay
            gameTime += deltaTime;
        }
    }
}
