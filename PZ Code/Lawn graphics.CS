using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

public class Zombie
{
    public string Name { get; set; }
    public float Health { get; set; }
    public int Row { get; set; }
    public float X { get; set; } // X-coordinate (pixels)
    public float MovementSpeed { get; set; } // Pixels per second
    public bool IsAlive { get; set; }

    public Zombie(string name, float health, int row, float x, float movementSpeed)
    {
        Name = name;
        Health = health;
        Row = row;
        X = x;
        MovementSpeed = movementSpeed;
        IsAlive = true;
    }

    public void Update(float deltaTime)
    {
        if (!IsAlive) return;

        X -= MovementSpeed * deltaTime; // Move left
        if (X <= 0)
        {
            X = 0;
            IsAlive = false; // Simulate reaching the house (game over in a real game)
        }
    }

    public void TakeDamage(float damage)
    {
        Health -= damage;
        if (Health <= 0)
        {
            Health = 0;
            IsAlive = false;
        }
    }

    public void Draw(Graphics g, float tileWidth, float tileHeight)
    {
        if (!IsAlive) return;
        float y = Row * tileHeight;
        g.FillRectangle(Brushes.Red, X, y, tileWidth / 2, tileHeight); // Draw zombie as a red rectangle
        g.DrawString($"HP: {Health}", new Font("Arial", 8), Brushes.Black, X, y);
    }
}

public class Pea
{
    public float X { get; set; }
    public float Y { get; set; }
    public float Speed { get; set; } // Pixels per second
    public int Row { get; set; }
    public float Damage { get; set; }
    public bool IsActive { get; set; }

    public Pea(float x, float y, float speed, int row, float damage)
    {
        X = x;
        Y = y;
        Speed = speed;
        Row = row;
        Damage = damage;
        IsActive = true;
    }

    public void Update(float deltaTime)
    {
        if (!IsActive) return;
        X += Speed * deltaTime; // Move right
    }

    public void Draw(Graphics g)
    {
        if (!IsActive) return;
        g.FillEllipse(Brushes.Green, X, Y, 10, 10); // Draw pea as a small green circle
    }
}

public class Plant
{
    public string Name { get; set; }
    public int Row { get; set; }
    public int Column { get; set; }
    public float X { get; set; }
    public float Y { get; set; }
    public float Damage { get; set; }
    public float FireRate { get; } = 1.5f; // Seconds between shots
    private float lastShotTime;

    public Plant(string name, int row, int column, float damage)
    {
        Name = name;
        Row = row;
        Column = column;
        Damage = damage;
        lastShotTime = 0;
    }

    public void Update(float deltaTime, List<Zombie> zombies, List<Pea> peas, float tileWidth, float tileHeight)
    {
        lastShotTime += deltaTime;
        if (lastShotTime >= FireRate)
        {
            // Find the first zombie in the same row, to the right of the plant
            Zombie target = zombies.Find(z => z.Row == Row && z.X >= X && z.IsAlive);
            if (target != null)
            {
                // Fire a pea
                float peaX = X + tileWidth / 2;
                float peaY = Y + tileHeight / 2 - 5; // Center vertically
                peas.Add(new Pea(peaX, peaY, 200, Row, Damage));
            }
            lastShotTime = 0;
        }
    }

    public void Draw(Graphics g, float tileWidth, float tileHeight)
    {
        g.FillEllipse(Brushes.LimeGreen, X, Y, tileWidth, tileHeight); // Draw plant as a green circle
        g.DrawString(Name, new Font("Arial", 8), Brushes.Black, X, Y);
    }
}

public class PvZ1LawnForm : Form
{
    private const int Rows = 5;
    private const int Columns = 9;
    private float tileWidth;
    private float tileHeight;
    private List<Plant> plants;
    private List<Zombie> zombies;
    private List<Pea> peas;
    private Timer gameTimer;
    private float lastUpdateTime;
    private Random random;

    public PvZ1LawnForm()
    {
        Width = 800;
        Height = 600;
        Text = "PvZ1 Lawn Simulation";
        DoubleBuffered = true; // Reduce flickering

        tileWidth = Width / (float)Columns;
        tileHeight = Height / (float)Rows;

        plants = new List<Plant>();
        zombies = new List<Zombie>();
        peas = new List<Pea>();
        random = new Random();

        // Place some Peashooters
        AddPlant(1, 1, new Plant("Peashooter", 1, 1, 20));
        AddPlant(3, 2, new Plant("Peashooter", 3, 2, 20));

        // Set up game timer
        gameTimer = new Timer();
        gameTimer.Interval = 16; // ~60 FPS
        gameTimer.Tick += GameLoop;
        gameTimer.Start();
        lastUpdateTime = (float)DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
    }

    private void AddPlant(int row, int column, Plant plant)
    {
        plant.X = column * tileWidth;
        plant.Y = row * tileHeight;
        plants.Add(plant);
    }

    private void SpawnZombie()
    {
        int row = random.Next(Rows);
        float x = (Columns - 1) * tileWidth;
        zombies.Add(new Zombie("Basic Zombie", 200, row, x, 50)); // 50 pixels/sec
    }

    private void GameLoop(object sender, EventArgs e)
    {
        float currentTime = (float)DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
        float deltaTime = currentTime - lastUpdateTime;
        lastUpdateTime = currentTime;

        // Spawn zombies occasionally
        if (random.NextDouble() < 0.02) // ~2% chance per frame
        {
            SpawnZombie();
        }

        // Update plants
        foreach (var plant in plants)
        {
            plant.Update(deltaTime, zombies, peas, tileWidth, tileHeight);
        }

        // Update peas
        foreach (var pea in peas)
        {
            pea.Update(deltaTime);

            // Check for collisions with zombies
            foreach (var zombie in zombies)
            {
                if (!zombie.IsAlive || !pea.IsActive) continue;
                if (pea.Row == zombie.Row && Math.Abs(pea.X - zombie.X) < tileWidth / 2)
                {
                    zombie.TakeDamage(pea.Damage);
                    pea.IsActive = false; // Pea disappears after hitting
                    break;
                }
            }

            // Remove peas that go off-screen
            if (pea.X > Width) pea.IsActive = false;
        }
        peas.RemoveAll(p => !p.IsActive);

        // Update zombies
        foreach (var zombie in zombies)
        {
            zombie.Update(deltaTime);
        }
        zombies.RemoveAll(z => !z.IsAlive);

        Invalidate(); // Trigger repaint
    }

    protected override void OnPaint(PaintEventArgs e)
    {
        Graphics g = e.Graphics;

        // Draw the lawn (grid)
        for (int row = 0; row < Rows; row++)
        {
            for (int col = 0; col < Columns; col++)
            {
                float x = col * tileWidth;
                float y = row * tileHeight;
                Brush tileColor = (row + col) % 2 == 0 ? Brushes.LawnGreen : Brushes.DarkGreen; // Alternating colors
                g.FillRectangle(tileColor, x, y, tileWidth, tileHeight);
                g.DrawRectangle(Pens.Black, x, y, tileWidth, tileHeight); // Grid lines
            }
        }

        // Draw plants
        foreach (var plant in plants)
        {
            plant.Draw(g, tileWidth, tileHeight);
        }

        // Draw peas
        foreach (var pea in peas)
        {
            pea.Draw(g);
        }

        // Draw zombies
        foreach (var zombie in zombies)
        {
            zombie.Draw(g, tileWidth, tileHeight);
        }
    }

    [STAThread]
    static void Main()
    {
        Application.Run(new PvZ1LawnForm());
    }
}
