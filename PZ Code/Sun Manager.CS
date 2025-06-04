using UnityEngine;
using UnityEngine.UI;

public class SunManager : MonoBehaviour
{
    public GameObject sunPrefab;          // Sun prefab to spawn
    public Transform[] sunSpawnPoints;    // Possible spawn points in the sky
    public float sunSpawnInterval = 10f;  // Time between sun spawns
    public float sunFallSpeed = 2f;       // Speed at which suns fall
    public float sunLifetime = 10f;       // Time before uncollected suns disappear
    public int sunValue = 25;             // Sun value when collected
    public Text sunCounterText;           // UI text to display sun count
    public float zombieSunDropChance = 0.1f; // Chance for zombies to drop sun on death

    private float lastSunSpawnTime;
    private int sunCount = 50;           // Starting sun amount (PvZ default)

    void Start()
    {
        UpdateSunCounterUI();
        lastSunSpawnTime = Time.time;
    }

    void Update()
    {
        // Spawn suns periodically
        if (Time.time >= lastSunSpawnTime + sunSpawnInterval && sunSpawnPoints.Length > 0)
        {
            SpawnSun();
            lastSunSpawnTime = Time.time;
        }
    }

    void SpawnSun()
    {
        // Choose a random spawn point
        Transform spawnPoint = sunSpawnPoints[Random.Range(0, sunSpawnPoints.Length)];
        GameObject sun = Instantiate(sunPrefab, spawnPoint.position, Quaternion.identity);
        
        // Add SunBehavior script
        SunBehavior sunBehavior = sun.AddComponent<SunBehavior>();
        sunBehavior.fallSpeed = sunFallSpeed;
        sunBehavior.lifetime = sunLifetime;
        sunBehavior.sunValue = sunValue;
        sunBehavior.manager = this;

        // Add collider for clicking
        SphereCollider collider = sun.GetComponent<SphereCollider>();
        if (collider == null)
        {
            collider = sun.AddComponent<SphereCollider>();
            collider.isTrigger = true;
            collider.radius = 0.5f;
        }
    }

    public void SpawnSunFromZombie(Vector3 position)
    {
        // Random chance to drop sun from zombie
        if (Random.value <= zombieSunDropChance)
        {
            GameObject sun = Instantiate(sunPrefab, position + Vector3.up * 1f, Quaternion.identity);
            SunBehavior sunBehavior = sun.AddComponent<SunBehavior>();
            sunBehavior.fallSpeed = sunFallSpeed;
            sunBehavior.lifetime = sunLifetime;
            sunBehavior.sunValue = sunValue;
            sunBehavior.manager = this;

            SphereCollider collider = sun.GetComponent<SphereCollider>();
            if (collider == null)
            {
                collider = sun.AddComponent<SphereCollider>();
                collider.isTrigger = true;
                collider.radius = 0.5f;
            }
        }
    }

    public void AddSun(int amount)
    {
        sunCount += amount;
        UpdateSunCounterUI();
    }

    void UpdateSunCounterUI()
    {
        if (sunCounterText != null)
        {
            sunCounterText.text = "Sun: " + sunCount;
        }
    }

    public bool SpendSun(int amount)
    {
        if (sunCount >= amount)
        {
            sunCount -= amount;
            UpdateSunCounterUI();
            return true;
        }
        return false;
    }

    public int GetSunCount()
    {
        return sunCount;
    }
}

public class SunBehavior : MonoBehaviour
{
    public float fallSpeed = 2f;
    public float lifetime = 10f;
    public int sunValue = 25;
    public SunManager manager;

    private float spawnTime;

    void Start()
    {
        spawnTime = Time.time;
    }

    void Update()
    {
        // Make sun fall slowly
        transform.Translate(Vector3.down * fallSpeed * Time.deltaTime);

        // Destroy sun if lifetime expires
        if (Time.time >= spawnTime + lifetime)
        {
            Destroy(gameObject);
        }
    }

    void OnMouseDown()
    {
        // Collect sun when clicked
        if (manager != null)
        {
            manager.AddSun(sunValue);
        }
        Destroy(gameObject);
    }
}
