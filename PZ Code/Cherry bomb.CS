using System;
using System.Collections.Generic;
using System.Threading;

class Zombie
{
    public string Name { get; set; }
    public double Health { get; set; }
    public int Row { get; set; }
    public int Column { get; set; }
    public double MovementSpeed { get; set; } // Units per second (columns per second)
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
            Console.WriteLine($"{Name} has been defeated!");
            return;
        }

        Column -= (int)(MovementSpeed * deltaTime); // Move left (columns decrease)
        if (Column < 0) Column = 0; // Prevent going off the lawn
        Console.WriteLine($"{Name} - Health: {Health:F0}, Position: (Row {Row}, Col {Column})");
    }

    public void TakeDamage(double damage)
    {
        Health -= damage;
        if (Health <= 0)
        {
            Health = 0;
            IsAlive = false;
            Console.WriteLine($"{Name} took {damage} damage and was defeated!");
        }
        else
        {
            Console.WriteLine($"{Name} took {damage} damage. Remaining Health: {Health:F0}");
        }
    }
}

class CherryBomb
{
    public string Name { get; } = "Cherry Bomb";
    public int SunCost { get; } = 150; // Cost to plant
    public double Damage { get; } = 1800; // Damage dealt
    public int BlastRadius { get; } = 1; // 3x3 area (1 unit in each direction from center)
    private int row;
    private int column;
    private bool hasExploded;

    public CherryBomb(int row, int column)
    {
        this.row = row;
        this.column = column;
        hasExploded = false;
    }

    public void Explode(List<Zombie> zombies)
    {
        if (hasExploded)
        {
            Console.WriteLine($"{Name} has already exploded!");
            return;
        }

        Console.WriteLine($"{Name} exploded at (Row {row}, Col {column})!");
        hasExploded = true;

        foreach (var zombie in zombies)
        {
            if (!zombie.IsAlive) continue;

            // Check if zombie is within the 3x3 blast radius
            int rowDiff = Math.Abs(zombie.Row - row);
            int colDiff = Math.Abs(zombie.Column - column);
            if (rowDiff <= BlastRadius && colDiff <= BlastRadius)
            {
                zombie.TakeDamage(Damage);
            }
        }
    }
}

class GameSimulation
{
    static void Main()
    {
        List<Zombie> zombies = new List<Zombie>
        {
            new Zombie("Basic Zombie", 200, 3, 5, 1.0), // Within blast radius
            new Zombie("Conehead Zombie", 370, 2, 4, 1.0), // Within blast radius
            new Zombie("Buckethead Zombie", 1100, 1, 6, 1.0) // Outside blast radius
        };

        CherryBomb cherryBomb = new CherryBomb(3, 3); // Plant at row 3, column 3

        double gameTime = 0;
        const double deltaTime = 1.0; // 1 second steps

        Console.WriteLine("Simulation started. Zombies advancing...");

        while (gameTime < 10) // Run simulation for 10 seconds
        {
            Console.WriteLine($"\nTime: {gameTime} seconds");

            // Explode Cherry Bomb at 3 seconds
            if (gameTime == 3)
            {
                cherryBomb.Explode(zombies);
            }

            // Update zombies
            foreach (var zombie in zombies)
            {
                zombie.Update(deltaTime);
            }

            Thread.Sleep(1000); // Simulate 1 second delay
            gameTime += deltaTime;
        }
    }
}
