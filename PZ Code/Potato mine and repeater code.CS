using System;

public class PotatoMine
{
    public int Health { get; private set; }
    public int Row { get; private set; }
    public int Column { get; private set; }
    public bool IsAlive => Health > 0;
    public bool IsArmed { get; private set; }
    private int ArmingTimeRemaining { get; set; }
    private const int ArmingDuration = 10; // Seconds to arm, scaled down from PvZ
    private const int ExplosionDamage = 1800; // High damage, kills most zombies

    public PotatoMine(int row, int column)
    {
        Health = 300; // Potato Mine's health
        Row = row;
        Column = column;
        IsArmed = false;
        ArmingTimeRemaining = ArmingDuration;
    }

    public void UpdateArming()
    {
        if (!IsArmed && IsAlive)
        {
            ArmingTimeRemaining--;
            Console.WriteLine($"Potato Mine at ({Row}, {Column}) arming... ({ArmingTimeRemaining}s left)");
            if (ArmingTimeRemaining <= 0)
            {
                IsArmed = true;
                Console.WriteLine($"Potato Mine at ({Row}, {Column}) is now armed!");
            }
        }
    }

    public void Explode(Zombie zombie)
    {
        if (IsAlive && IsArmed && zombie.IsAlive && Row == zombie.Row && Column == zombie.Column)
        {
            zombie.TakeDamage(ExplosionDamage);
            Console.WriteLine($"Potato Mine at ({Row}, {Column}) exploded, dealing {ExplosionDamage} damage to zombie!");
            Health = 0; // Potato Mine destroys itself
            Console.WriteLine($"Potato Mine at ({Row}, {Column}) has been destroyed!");
        }
    }

    public void TakeDamage(int damage)
    {
        if (IsAlive)
        {
            Health -= damage;
            Console.WriteLine($"Potato Mine at ({Row}, {Column}) took {damage} damage. Remaining health: {Health}");
            if (!IsAlive)
            {
                Console.WriteLine($"Potato Mine at ({Row}, {Column}) has been destroyed!");
            }
        }
    }
}

public class Repeater
{
    public int Health { get; private set; }
    public int Row { get; private set; }
    public int Column { get; private set; }
    public bool IsAlive => Health > 0;
    private const int PeaDamage = 20; // Damage per pea, Repeater shoots 2 peas
    private const int AttackCooldown = 2; // Seconds between attack cycles
    private int CooldownRemaining { get; set; }

    public Repeater(int row, int column)
    {
        Health = 300; // Repeater's health
        Row = row;
        Column = column;
        CooldownRemaining = 0;
    }

    public void Attack(Zombie[] zombies)
    {
        if (IsAlive && CooldownRemaining <= 0)
        {
            // Find the closest zombie in the same row
            Zombie target = null;
            int minColumn = int.MaxValue;
            foreach (var zombie in zombies)
            {
                if (zombie.IsAlive && zombie.Row == Row && zombie.Column > Column && zombie.Column < minColumn)
                {
                    target = zombie;
                    minColumn = zombie.Column;
                }
            }

            if (target != null)
            {
                // Shoot two peas
                for (int i = 1; i <= 2; i++)
                {
                    target.TakeDamage(PeaDamage);
                    Console.WriteLine($"Repeater at ({Row}, {Column}) shot pea {i} at zombie at ({target.Row}, {target.Column}) for {PeaDamage} damage!");
                }
                CooldownRemaining = AttackCooldown;
            }
        }
        else if (CooldownRemaining > 0)
        {
            CooldownRemaining--;
        }
    }

    public void TakeDamage(int damage)
    {
        if (IsAlive)
        {
            Health -= damage;
            Console.WriteLine($"Repeater at ({Row}, {Column}) took {damage} damage. Remaining health: {Health}");
            if (!IsAlive)
            {
                Console.WriteLine($"Repeater at ({Row}, {Column}) has been destroyed!");
            }
        }
    }
}

public class Zombie
{
    public int Health { get; private set; }
    public int Row { get; private set; }
    public int Column { get; private set; }
    public int Damage { get; private set; }
    public bool IsAlive => Health > 0;

    public Zombie(int row, int column)
    {
        Health = 200; // Basic zombie health
        Row = row;
        Column = column;
        Damage = 100; // Damage per attack
    }

    public void Move()
    {
        if (IsAlive)
        {
            Column--; // Move left
            Console.WriteLine($"Zombie moved to ({Row}, {Column})");
        }
    }

    public void Attack(PotatoMine potatoMine)
    {
        if (IsAlive && potatoMine.IsAlive && Row == potatoMine.Row && Column == potatoMine.Column)
        {
            potatoMine.TakeDamage(Damage);
        }
    }

    public void Attack(Repeater repeater)
    {
        if (IsAlive && repeater.IsAlive && Row == repeater.Row && Column == repeater.Column)
        {
            repeater.TakeDamage(Damage);
        }
    }

    public void TakeDamage(int damage)
    {
        if (IsAlive)
        {
            Health -= damage;
            Console.WriteLine($"Zombie at ({Row}, {Column}) took {damage} damage. Remaining health: {Health}");
            if (!IsAlive)
            {
                Console.WriteLine($"Zombie at ({Row}, {Column}) has been destroyed!");
            }
        }
    }
}

public class Game
{
    public static void Main()
    {
        // Place a Potato Mine at (1, 5)
        PotatoMine potatoMine = new PotatoMine(1, 5);
        // Place a Repeater at (2, 3)
        Repeater repeater = new Repeater(2, 3);
        // Place zombies: one for Potato Mine (1, 6), one for Repeater (2, 8)
        Zombie[] zombies = new Zombie[]
        {
            new Zombie(1, 6), // For Potato Mine
            new Zombie(2, 8)  // For Repeater
        };

        Console.WriteLine("Starting PvZ Potato Mine and Repeater simulation...");

        // Simple game loop
        int seconds = 0;
        while ((potatoMine.IsAlive || repeater.IsAlive) && zombies.Any(z => z.IsAlive))
        {
            Console.WriteLine($"\nTime: {seconds}s");

            // Update Potato Mine
            potatoMine.UpdateArming();
            foreach (var zombie in zombies)
            {
                if (zombie.IsAlive && zombie.Row == potatoMine.Row && zombie.Column == potatoMine.Column)
                {
                    potatoMine.Explode(zombie);
                }
            }

            // Update Repeater
            repeater.Attack(zombies);

            // Update Zombies
            foreach (var zombie in zombies)
            {
                if (zombie.IsAlive)
                {
                    zombie.Move();
                    zombie.Attack(potatoMine);
                    zombie.Attack(repeater);
                }
            }

            System.Threading.Thread.Sleep(1000); // 1 second per tick
            seconds++;
        }

        Console.WriteLine("Simulation ended.");
    }
}
