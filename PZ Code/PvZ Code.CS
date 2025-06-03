using UnityEngine;

public class PeaShooter : MonoBehaviour
{
    public GameObject peaPrefab;  // The pea prefab to be instantiated
    public Transform shootPoint;   // Point where peas are spawned (e.g., barrel of the plant)
    public float shootCooldown = 1.5f;  // Time between shots (PvZ-style pacing)
    public float peaSpeed = 10f;       // Speed of the pea projectile
    public float peaDamage = 20f;      // Damage dealt by each pea
    public float detectionRange = 10f;  // Range to detect zombies
    public LayerMask zombieLayer;      // Layer for zombies to detect
    public AudioClip shootSound;       // Sound effect for shooting
    public ParticleSystem muzzleFlash;  // Optional particle effect for shooting

    private float lastShootTime;       // Tracks last time a pea was shot
    private Animator animator;         // For plant shooting animation
    private AudioSource audioSource;   // For playing shoot sound

    void Start()
    {
        // Get components
        animator = GetComponent<Animator>();
        audioSource = GetComponent<AudioSource>();
        
        // Ensure AudioSource is set up if shootSound is assigned
        if (shootSound != null && audioSource == null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
        }
    }

    void Update()
    {
        // Check if there’s a zombie in range and if cooldown has elapsed
        if (CanShoot())
        {
            Shoot();
        }
    }

    bool CanShoot()
    {
        // Check cooldown
        if (Time.time < lastShootTime + shootCooldown)
        {
            return false;
        }

        // Check for zombies in range using a raycast
        RaycastHit hit;
        if (Physics.Raycast(transform.position, Vector3.forward, out hit, detectionRange, zombieLayer))
        {
            return true; // Zombie detected in range
        }

        return false; // No zombie in range
    }

    void Shoot()
    {
        // Update last shoot time
        lastShootTime = Time.time;

        // Play shooting animation if animator exists
        if (animator != null)
        {
            animator.SetTrigger("Shoot");
        }

        // Play shoot sound if assigned
        if (audioSource != null && shootSound != null)
        {
            audioSource.PlayOneShot(shootSound);
        }

        // Play muzzle flash particle effect if assigned
        if (muzzleFlash != null)
        {
            muzzleFlash.Play();
        }

        // Instantiate a pea at the shoot point (or slightly forward from plant)
        Vector3 spawnPosition = shootPoint != null ? shootPoint.position : transform.position + Vector3.forward * 0.5f;
        GameObject pea = Instantiate(peaPrefab, spawnPosition, Quaternion.identity);

        // Add a Rigidbody to the pea (for basic physics)
        Rigidbody rb = pea.GetComponent<Rigidbody>();
        if (rb == null)
        {
            rb = pea.AddComponent<Rigidbody>();
        }
        rb.useGravity = false; // Peas don’t fall in PvZ
        rb.velocity = Vector3.forward * peaSpeed;

        // Add Pea script to handle damage (see below)
        Pea peaScript = pea.AddComponent<Pea>();
        peaScript.damage = peaDamage;

        // Destroy the pea after a few seconds
        Destroy(pea, 5f);
    }
}

// Separate script for the pea to handle collision and damage
public class Pea : MonoBehaviour
{
    public float damage = 20f; // Damage dealt to zombies

    void OnCollisionEnter(Collision collision)
    {
        // Check if the collision is with a zombie (based on tag or layer)
        if (collision.gameObject.CompareTag("Zombie"))
        {
            // Apply damage to zombie (assumes zombie has a health script)
            ZombieHealth zombieHealth = collision.gameObject.GetComponent<ZombieHealth>();
            if (zombieHealth != null)
            {
                zombieHealth.TakeDamage(damage);
            }

            // Destroy the pea on impact
            Destroy(gameObject);
        }
    }
}

// Basic ZombieHealth script for reference
public class ZombieHealth : MonoBehaviour
{
    public float health = 100f;

    public void TakeDamage(float damage)
    {
        health -= damage;
        if (health <= 0)
        {
            Destroy(gameObject); // Zombie dies
        }
    }
}
