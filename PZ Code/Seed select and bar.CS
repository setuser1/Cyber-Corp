using System;
using System.Collections.Generic;
using System.Linq;

public class Plant
{
    public string Name { get; private set; }
    public int SunCost { get; private set; }

    public Plant(string name, int sunCost)
    {
        Name = name;
        SunCost = sunCost;
    }

    public override string ToString()
    {
        return $"{Name} (Cost: {SunCost} sun)";
    }
}

public class SeedSelectionScreen
{
    private List<Plant> availablePlants;
    private List<Plant> selectedPlants;
    private const int MaxSeeds = 6; // PvZ typically allows 6 seed packets

    public SeedSelectionScreen()
    {
        // Initialize available plants (example set based on PvZ)
        availablePlants = new List<Plant>
        {
            new Plant("Peashooter", 100),
            new Plant("Sunflower", 50),
            new Plant("Wall-nut", 50),
            new Plant("Potato Mine", 25),
            new Plant("Chomper", 150),
            new Plant("Repeater", 200)
        };
        selectedPlants = new List<Plant>();
    }

    public List<Plant> SelectPlants()
    {
        Console.WriteLine("=== Plant Seed Selection Screen ===");
        while (selectedPlants.Count < MaxSeeds)
        {
            Console.WriteLine("\nAvailable Plants:");
            for (int i = 0; i < availablePlants.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {availablePlants[i]}");
            }
            Console.WriteLine($"Selected {selectedPlants.Count}/{MaxSeeds} plants.");
            Console.Write("Enter plant number to select (or 'done' to finish early): ");

            string input = Console.ReadLine().Trim().ToLower();
            if (input == "done" && selectedPlants.Count > 0)
            {
                break;
            }

            if (int.TryParse(input, out int choice) && choice >= 1 && choice <= availablePlants.Count)
            {
                Plant selected = availablePlants[choice - 1];
                if (!selectedPlants.Contains(selected))
                {
                    selectedPlants.Add(selected);
                    Console.WriteLine($"Selected {selected.Name}!");
                }
                else
                {
                    Console.WriteLine($"{selected.Name} is already selected!");
                }
            }
            else
            {
                Console.WriteLine("Invalid input. Enter a number or 'done'.");
            }
        }

        Console.WriteLine("\nSeed selection complete!");
        return selectedPlants;
    }
}

public class SeedBar
{
    private List<Plant> plants;

    public SeedBar(List<Plant> selectedPlants)
    {
        plants = selectedPlants;
    }

    public void Display()
    {
        Console.WriteLine("\n=== Seed Bar ===");
        if (plants.Count == 0)
        {
            Console.WriteLine("No plants selected.");
        }
        else
        {
            for (int i = 0; i < plants.Count; i++)
            {
                Console.WriteLine($"Slot {i + 1}: {plants[i]}");
            }
        }
    }

    public void SimulatePlanting()
    {
        Console.WriteLine("\n=== Planting Simulation ===");
        Console.Write("Enter slot number to plant (or 'exit' to stop): ");
        string input = Console.ReadLine().Trim().ToLower();

        while (input != "exit")
        {
            if (int.TryParse(input, out int slot) && slot >= 1 && slot <= plants.Count)
            {
                Plant plant = plants[slot - 1];
                Console.WriteLine($"Planting {plant.Name} (Cost: {plant.SunCost} sun) at a chosen tile!");
                // Simulate sun cost deduction (not implemented fully)
                Console.WriteLine($"Remaining sun: (not tracked in this simulation)");
            }
            else
            {
                Console.WriteLine("Invalid slot number.");
            }
            Console.Write("Enter slot number to plant (or 'exit' to stop): ");
            input = Console.ReadLine().Trim().ToLower();
        }
    }
}

public class Game
{
    public static void Main()
    {
        Console.WriteLine("Starting PvZ Seed Selection and Seed Bar simulation...");

        // Initialize seed selection screen
        SeedSelectionScreen selectionScreen = new SeedSelectionScreen();
        List<Plant> selectedPlants = selectionScreen.SelectPlants();

        // Initialize seed bar with selected plants
        SeedBar seedBar = new SeedBar(selectedPlants);
        seedBar.Display();

        // Simulate planting from seed bar
        seedBar.SimulatePlanting();

        Console.WriteLine("\nSimulation ended.");
    }
}
