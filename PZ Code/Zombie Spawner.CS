using UnityEngine;
using System.Collections.Generic;

public class ZombieSpawner : MonoBehaviour
{
    public GameObject[] zombiePrefabs;  // Array of zombie prefabs to spawn
    public Transform[] spawnPoints;     // Array of spawn points (e.g., at the edge of the lane)
    public float spawnInterval = 5f;    // Time between zombie spawns
    public float minSpawnInterval = 2f; // Minimum spawn interval as game progresses
    public float spawnIntervalDecrease = 0.1f; // How much spawn interval decreases per wave
    public float zombieSpeed = 1f;      // Base speed for zombies
    public float zombieHealth = 100f;   // Base health for zombies
    public int maxZombies = 10;         // Maximum zombies in the scene at once

    private float lastSpawnTime;        // Tracks last spawn time
    private float currentSpawnInterval; // Current spawn interval
    private List<GameObject> activeZombies; // Tracks active zombies

    void Start()
    {
        currentSpawnInterval = spawnInterval;
        activeZombies = new List<GameObject>();
        lastSpawnTime = Time.time; // Start spawning immediately
    }

    void Update()
    {
        // Clean up destroyed zombies from the list
        activeZombies.RemoveAll(zombie => zombie == null);

        // Check if we can spawn a new zombie
        if (CanSpawnZombie())
        {
            SpawnZombie();
            lastSpawnTime = Time.time;
        }

        // Gradually decrease spawn interval to increase difficulty
        if (currentSpawnInterval > minSpawnInterval)
        {
            currentSpawnInterval -= spawnIntervalDecrease * Time.deltaTime;
            currentSpawnInterval = Mathf.Max(currentSpawnInterval, minSpawnInterval);
        }
    }

    bool CanSpawnZombie()
    {
        return Time.time >= lastSpawnTime + currentSpawnInterval && activeZombies.Count < maxZombies;
    }

    void SpawnZombie()
    {
        // Choose a random spawn point
        if (spawnPoints.Length == 0)
        {
            Debug.LogWarning("No spawn points assigned to ZombieSpawner!");
            return;
        }
        Transform spawnPoint = spawnPoints[Random.Range(0, spawnPoints.Length)];

        // Choose a random zombie prefab
        if (zombiePrefabs.Length == 0)
        {
            Debug.LogWarning("No zombie prefabs assigned to ZombieSpawner!");
            return;
        }
        GameObject zombiePrefab = zombiePrefabs[Random.Range(0, zombiePrefabs.Length)];

        // Instantiate zombie
        GameObject zombie = Instantiate(zombiePrefab, spawnPoint.position, Quaternion.identity);

        // Add ZombieHealth component if not already present
        ZombieHealth zombieHealthComponent = zombie.GetComponent<ZombieHealth>();
        if (zombieHealthComponent == null)
        {
            zombieHealthComponent = zombie.AddComponent<ZombieHealth>();
        }
        zombieHealthComponent.health = zombieHealth;

        // Add ZombieMovement component
        ZombieMovement zombieMovement = zombie.GetComponent<ZombieMovement>();
        if (zombieMovement == null)
        {
            zombieMovement = zombie.AddComponent<ZombieMovement>();
        }
        zombieMovement.speed = zombieSpeed;

        // Tag the zombie for pea collision detection
        zombie.tag = "Zombie";

        // Add to active zombies list
        activeZombies.Add(zombie);
    }
}

// Script to handle zombie movement
public class ZombieMovement : MonoBehaviour
{
    public float speed = 1f;

    void Update()
    {
        // Move zombie forward (toward plants, assuming Z-axis is forward)
        transform.Translate(Vector3.back * speed * Time.deltaTime);

        // Optional: Destroy zombie if it goes too far (e.g., past the plants)
        if (transform.position.z < -10f) // Adjust based on your game layout
        {
            Destroy(gameObject);
        }
    }
}
