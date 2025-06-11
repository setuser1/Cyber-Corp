using System;

public class WallNut
{
    public int Health { get; private set; }
    public int Row { get; private set; }
    public int Column { get; private set; }
    public bool IsAlive => Health > 0;

    public WallNut(int row, int column)
    {
        Health = 4000; // Wall-nut's health, based on PvZ (4000 damage points)
        Row = row;
        Column = column;
    }

    public void TakeDamage(int damage)
    {
        if (IsAlive)
        {
            Health -= damage;
            Console.WriteLine($"Wall-nut at ({Row}, {Column}) took {damage} damage. Remaining health: {Health}");
            if (!IsAlive)
            {
                Console.WriteLine($"Wall-nut at ({Row}, {Column}) has been destroyed!");
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

    public void Attack(WallNut wallNut)
    {
        if (IsAlive && wallNut.IsAlive && Row == wallNut.Row && Column == wallNut.Column)
        {
            wallNut.TakeDamage(Damage);
        }
    }
}

public class Game
{
    public static void Main()
    {
        // Place a Wall-nut at position (1, 5)
        WallNut wallNut = new WallNut(1, 5);
        // Place a zombie at the same position to simulate combat
        Zombie zombie = new Zombie(1, 5);

        Console.WriteLine("Starting PvZ Wall-nut simulation...");

        // Simple game loop
        while (wallNut.IsAlive && zombie.IsAlive)
        {
            zombie.Attack(wallNut);
            // Pause for readability
            System.Threading.Thread.Sleep(1000);
        }

        Console.WriteLine("Simulation ended.");
    }
}
