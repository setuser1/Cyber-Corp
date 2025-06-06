using System;
using System.Collections.Generic;
using System.Threading;

class Plant
{
    public string Name { get; set; }
    public int Row { get; set; }
    public int Column { get; set; }
    public double Damage { get; set; } // Damage per second
    public double FireRate { get; } = 1.5; // Seconds between shots
    private double lastShotTime;

    public Plant(string name, int row, int column, double damage)
    {
        Name = name;
        Row = row;
        Column = column;
        Damage = damage;
        lastShotTime = 0;
    }

    public void Update(double deltaTime, List<Zombie> zombies)
    {
        lastShotTime += deltaTime;
        if (lastShotTime >= FireRate)
        {
            // Find the first zombie in the same row, to the right of the plant
            Zombie target = zombies.Find(z => z.Row == Row && z.Column >= Column && z.IsAlive);
            if (target != null)
            {
                target.TakeDamage(Damage);
                Console.WriteLine($"{Name} at (Row {Row}, Col {Column}) shot {target.Name} for {Damage} damage!");
            }
            lastShotTime = 0; // Reset timer
        }
    }
}

class Zombie
{
    public string Name { get; set; }
    public double Health { get; set; }
    public int Row { get; set; }
    public int Column { get; set; }
    public double MovementSpeed { get; set; } // Columns per second
    public bool IsAlive { get; set; }

    public Zombie(string name, double health, int row, int column, double movementSpeed)
    {
        Name = name;
        Health = health;
        Row = row;
        Column = column;
        MovementSpeed = movementSpeed;
        IsAlive = true;
    }

    public void Update(double deltaTime)
    {
        if (!IsAlive)
        {
            return;
        }

        Column -= (int)(MovementSpeed * deltaTime); // Move left
        if (Column < 0)
        {
            Column = 0;
            Console.WriteLine($"{Name} reached the house! Game Over!");
            Environment.Exit(0); // End simulation
        }
    }

    public void TakeDamage(double damage)
    {
        Health -= damage;
        if (Health <= 0)
        {
            Health = 0;
            IsAlive = false;
            Console.WriteLine($"{Name} was defeated!");
        }
        else
        {
            Console.WriteLine($"{Name} took {damage} damage. Remaining Health: {Health:F0}");
        }
    }
}

class Lawn
{
    private const int Rows = 5;
    private const int Columns = 9;
    private Plant[,] grid; // Grid to store plants
    private List<Zombie> zombies;
    private Random random;

    public Lawn()
    {
        grid = new Plant[Rows, Columns];
        zombies = new List<Zombie>();
        random = new Random();
    }

    public void PlantSeed(int row, int column, Plant plant)
    {
        if (row < 0 || row >= Rows || column < 0 || column >= Columns)
        {
            Console.WriteLine($"Invalid position: (Row {row}, Col {column})");
            return;
        }

        if (grid[row, column] != null)
        {
            Console.WriteLine($"A plant is already at (Row {row}, Col {column})!");
            return;
        }

        plant.Row = row;
        plant.Column = column;
        grid[row, column] = plant;
        Console.WriteLine($"Planted {plant.Name} at (Row {row}, Col {column})");
    }

    public void SpawnZombie(string name, double health, double movementSpeed)
    {
        int row = random.Next(Rows); // Random row
        int column = Columns - 1; // Start at the rightmost column
        Zombie zombie = new Zombie(name, health, row, column, movementSpeed);
        zombies.Add(zombie);
        Console.WriteLine($"{zombie.Name} spawned at (Row {row}, Col {column})");
    }

    public void Update(double deltaTime)
    {
        // Update plants
        for (int row = 0; row < Rows; row++)
        {
            for (int col = 0; col < Columns; col++)
            {
                if (grid[row, col] != null)
                {
                    grid[row, col].Update(deltaTime, zombies);
                }
            }
        }

        // Update zombies
        foreach (var zombie in zombies)
        {
            if (zombie.IsAlive)
            {
                zombie.Update(deltaTime);
            }
        }

        // Remove defeated zombies
        zombies.RemoveAll(z => !z.IsAlive);

        // Display lawn state
        Display();
    }

    private void Display()
    {
        Console.WriteLine("\nLawn State:");
        for (int row = 0; row < Rows; row++)
        {
            string rowDisplay = $"Row {row}: ";
            for (int col = 0; col < Columns; col++)
            {
                bool hasPlant = grid[row, col] != null;
                bool hasZombie = zombies.Exists(z => z.Row == row && z.Column == col && z.IsAlive);
                if (hasPlant && hasZombie)
                {
                    rowDisplay += "[P+Z] ";
                }
                else if (hasPlant)
                {
                    rowDisplay += "[P] ";
                }
                else if (hasZombie)
                {
                    rowDisplay += "[Z] ";
                }
                else
                {
                    rowDisplay += "[ ] ";
                }
            }
            Console.WriteLine(rowDisplay);
        }
    }
}

class GameSimulation
{
    static void Main()
    {
        Lawn lawn = new Lawn();

        // Plant some Peashooters
        lawn.PlantSeed(1, 1, new Plant("Peashooter", 1, 1, 20)); // 20 damage per shot
        lawn.PlantSeed(3, 2, new Plant("Peashooter", 3, 2, 20));

        double gameTime = 0;
        const double deltaTime = 1.0; // 1 second steps

        Console.WriteLine("Simulation started...");

        while (gameTime < 20) // Run simulation for 20 seconds
        {
            Console.WriteLine($"\nTime: {gameTime} seconds");

            // Spawn zombies at specific times
            if (gameTime == 0 || gameTime == 5)
            {
                lawn.SpawnZombie("Basic Zombie", 200, 1.0);
            }

            lawn.Update(deltaTime);
            Thread.Sleep(1000); // Simulate 1 second delay
            gameTime += deltaTime;
        }
    }
}
