public class Chomper
{
    public int Health { get; private set; }
    public int Row { get; private set; }
    public int Column { get; private set; }
    public bool IsAlive => Health > 0;
    private bool IsChewing { get; set; }
    private int ChewTimeRemaining { get; set; }
    private const int ChewDuration = 3; // Seconds to chew, based on PvZ (approx. 40s scaled down)
    private const int AttackDamage = 1000; // High damage to simulate eating a zombie

    public Chomper(int row, int column)
    {
        Health = 1500; // Chomper's health, based on PvZ
        Row = row;
        Column = column;
        IsChewing = false;
        ChewTimeRemaining = 0;
    }

    public void Attack(Zombie zombie)
    {
        if (IsAlive && !IsChewing && zombie.IsAlive && Row == zombie.Row && Column + 1 == zombie.Column)
        {
            zombie.TakeDamage(AttackDamage);
            Console.WriteLine($"Chomper at ({Row}, {Column}) ate zombie at ({zombie.Row}, {zombie.Column}) for {AttackDamage} damage!");
            IsChewing = true;
            ChewTimeRemaining = ChewDuration;
        }
    }

    public void UpdateChewing()
    {
        if (IsChewing)
        {
            ChewTimeRemaining--;
            Console.WriteLine($"Chomper at ({Row}, {Column}) is chewing... ({ChewTimeRemaining}s left)");
            if (ChewTimeRemaining <= 0)
            {
                IsChewing = false;
                Console.WriteLine($"Chomper at ({Row}, {Column}) finished chewing and is ready to attack!");
            }
        }
    }

    public void TakeDamage(int damage)
    {
        if (IsAlive)
        {
            Health -= damage;
            Console.WriteLine($"Chomper at ({Row}, {Column}) took {damage} damage. Remaining health: {Health}");
            if (!IsAlive)
            {
                Console.WriteLine($"Chomper at ({Row}, {Column}) has been destroyed!");
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
public void Attack(Chomper chomper)
    {
        if (IsAlive && chomper.IsAlive && Row == chomper.Row && Column == chomper.Column)
        {
            chomper.TakeDamage(Damage);
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
        // Place a Chomper at position (1, 4)
        Chomper chomper = new Chomper(1, 4);
        // Place a zombie in front of the Chomper at (1, 5)
        Zombie zombie = new Zombie(1, 5);

        Console.WriteLine("Starting PvZ Chomper simulation...");

        // Simple game loop
        int seconds = 0;
        while (chomper.IsAlive && zombie.IsAlive)
        {
            Console.WriteLine($"\nTime: {seconds}s");
            chomper.Attack(zombie);
            if (zombie.IsAlive)
            {
                // Zombie moves left if not blocked or eaten
                zombie = new Zombie(zombie.Row, zombie.Column - 1);
                Console.WriteLine($"Zombie moved to ({zombie.Row}, {zombie.Column})");
                zombie.Attack(chomper);
            }
            chomper.UpdateChewing();
            System.Threading.Thread.Sleep(1000); // 1 second per tick
            seconds++;
        }

        Console.WriteLine("Simulation ended.");
    }
