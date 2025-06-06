using System;
using System.Threading;

class PoleVaultingZombie
{
    public string Name { get; set; }
    public double Health { get; set; }
    public double MovementSpeed { get; set; } // Units per second
    public double AttackSpeed { get; set; } // Attacks per second
    public double DistanceTraveled { get; set; }
    public bool HasVaulted { get; set; }
    private double originalMovementSpeed;
    private double vaultDistance;

    public PoleVaultingZombie(string name, double health, double movementSpeed, double attackSpeed, double vaultDistance)
    {
        Name = name;
        Health = health;
        MovementSpeed = movementSpeed;
        AttackSpeed = attackSpeed;
        DistanceTraveled = 0;
        HasVaulted = false;
        originalMovementSpeed = movementSpeed;
        this.vaultDistance = vaultDistance;
    }

    public void Update(double deltaTime)
    {
        if (Health <= 0)
        {
            Console.WriteLine($"{Name} has been defeated!");
            return;
        }

        // Check for vaulting condition (e.g., encountering a plant at 5 units)
        if (!HasVaulted && DistanceTraveled >= 5)
        {
            PerformVault();
        }

        // Move forward
        DistanceTraveled += MovementSpeed * deltaTime;
        Console.WriteLine($"{Name} - Health: {Health:F0}, Distance Traveled: {DistanceTraveled:F1} units, Speed: {MovementSpeed:F2} units/sec");
    }

    public void TakeDamage(double damage)
    {
        Health -= damage;
        if (Health < 0) Health = 0;
        Console.WriteLine($"{Name} took {damage} damage. Remaining Health: {Health:F0}");
    }

    private void PerformVault()
    {
        HasVaulted = true;
        DistanceTraveled += vaultDistance; // Instant jump forward
        MovementSpeed = 0.5; // Slow down after vaulting
        Console.WriteLine($"{Name} vaulted over a plant! Jumped {vaultDistance} units, now moving at {MovementSpeed} units/sec");
    }
}

class GameSimulation
{
    static void Main()
    {
        PoleVaultingZombie zombie = new PoleVaultingZombie("Pole Vaulting Zombie", 500, 1.2, 0.5, 2.0);

        double gameTime = 0;
        const double deltaTime = 1.0; // 1 second steps
        const double damagePerSecond = 20.0; // Simulated pea shooter damage

        Console.WriteLine("Simulation started. Pole Vaulting Zombie advancing...");

        while (gameTime < 20) // Run simulation for 20 seconds
        {
            Console.WriteLine($"\nTime: {gameTime} seconds");

            zombie.Update(deltaTime);
            if (zombie.Health > 0)
            {
                zombie.TakeDamage(damagePerSecond * deltaTime); // Apply damage
            }

            Thread.Sleep(1000); // Simulate 1 second delay
            gameTime += deltaTime;
        }
    }
}
