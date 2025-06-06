class Sunflower
{
    public string Name { get; } = "Sunflower";
    public int SunCost { get; } = 50; // Cost to plant
    public double SunProductionRate { get; } = 24.0; // Seconds between sun production
    public int SunValue { get; } = 25; // Sun produced each time
    private double lastSunProductionTime;

    public Sunflower()
    {
        lastSunProductionTime = 0;
    }

    public int Update(double deltaTime)
    {
        int sunProduced = 0;
        lastSunProductionTime += deltaTime;

        if (lastSunProductionTime >= SunProductionRate)
        {
            sunProduced += SunValue;
            Console.WriteLine($"{Name} produced {SunValue} sun!");
            lastSunProductionTime = 0; // Reset timer
        }

        return sunProduced;
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
        Sunflower sunflower = new Sunflower();

        double gameTime = 0;
        int totalSun = 50; // Starting sun
        const double deltaTime = 1.0; // 1 second steps

        Console.WriteLine($"Starting with {totalSun} sun.");

        while (gameTime < 30) // Run simulation for 30 seconds
        {
            Console.WriteLine($"\nTime: {gameTime} seconds");

            // Update Sunflower and collect sun
            totalSun += sunflower.Update(deltaTime);

            // Update Snow Pea and zombies
            snowPea.Update(deltaTime, zombies);
            foreach (var zombie in zombies)
            {
                zombie.Update(deltaTime);
            }

            Console.WriteLine($"Total Sun: {totalSun}");
            Thread.Sleep(1000); // Simulate 1 second delay
            gameTime += deltaTime;
        }
    }
}
