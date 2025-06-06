using System;
using System.Collections.Generic;
using System.Threading;

class Zombie
{
    public string Name { get; set; }
    public double MovementSpeed { get; set; } // Units per second
    public double AttackSpeed { get; set; } // Attacks per second
    private double originalMovementSpeed;
    private double originalAttackSpeed;
    public bool IsSlowed { get; set; }
    public double SlowDuration { get; set; } // Seconds remaining for slowdown

    public Zombie(string name, double movementSpeed, double attackSpeed)
    {
        Name = name;
        MovementSpeed = movementSpeed;
        AttackSpeed = attackSpeed;
        originalMovementSpeed = movementSpeed;
        originalAttackSpeed = attackSpeed;
        IsSlowed = false;
        SlowDuration = 0;
    }

    public void Update(double deltaTime)
    {
        if (IsSlowed)
        {
            SlowDuration -= deltaTime;
            if (SlowDuration <= 0)
            {
                ResetSpeed();
            }
        }
        Console.WriteLine($"{Name} - Movement Speed: {MovementSpeed:F2}, Attack Speed: {AttackSpeed:F2}");
    }

    public void ApplySlowdown(double slowPercentage, double duration)
    {
        if (!IsSlowed || SlowDuration < duration)
        {
            MovementSpeed = originalMovementSpeed * (1 - slowPercentage);
            AttackSpeed = originalAttackSpeed * (1 - slowPercentage);
            IsSlowed = true;
            SlowDuration = duration;
            Console.WriteLine($"{Name} has been slowed by {slowPercentage * 100}% for {duration} seconds!");
        }
    }

    private void ResetSpeed()
    {
        MovementSpeed = originalMovementSpeed;
        AttackSpeed = originalAttackSpeed;
        IsSlowed = false;
        SlowDuration = 0;
        Console.WriteLine($"{Name} speed has returned to normal!");
    }
}

class SnowPea
{
    public string Name { get; } = "Snow Pea";
    public int SunCost { get; } = 150; // Cost in sun (Versus Mode value)
    public double FireRate { get; } = 1.5; // Seconds between shots
    private double lastShotTime;
    private Random random;

    public SnowPea()
    {
        lastShotTime = 0;
        random = new Random();
    }

    public void Update(double deltaTime, List<Zombie> zombies)
    {
        lastShotTime += deltaTime;
        if (lastShotTime >= FireRate)
        {
            if (zombies.Count > 0)
            {
                int targetIndex = random.Next(zombies.Count);
                Zombie target = zombies[targetIndex];
                ApplySlowdownEffect(target);
            }
            lastShotTime = 0; // Reset timer
        }
    }

    private void ApplySlowdownEffect(Zombie zombie)
    {
        const double slowPercentage = 0.5; // 50% slowdown
        const double duration = 10.0; // 10 seconds slowdown
        zombie.ApplySlowdown(slowPercentage, duration);
    }
}

class GameSimulation
{
    static void Main()
    {
        List<Zombie> zombies = new List<Zombie>
        {
            new Zombie("Basic Zombie", 1.0, 0.5),
            new Zombie("Conehead Zombie", 1.0, 0.5)
        };
        SnowPea snowPea = new SnowPea();

        double gameTime = 0;
        const double deltaTime = 1.0; // 1 second steps for simplicity

        while (gameTime < 20) // Run simulation for 20 seconds
        {
            Console.WriteLine($"\nTime: {gameTime} seconds");
            snowPea.Update(deltaTime, zombies);

            foreach (var zombie in zombies)
            {
                zombie.Update(deltaTime);
            }

            Thread.Sleep(1000); // Simulate 1 second delay
            gameTime += deltaTime;
        }
    }
}
