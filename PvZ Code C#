using UnityEngine;

public class PeaShooter : MonoBehaviour
{
    public GameObject peaPrefab;  // The pea prefab to be instantiated

    // ... other variables ...

    void Update()
    {
        if (Input.GetMouseButtonDown(0))  // Example:  Shoot when left mouse button is clicked
        {
            // Instantiate a pea
            GameObject pea = Instantiate(peaPrefab, transform.position + Vector3.forward, Quaternion.identity);

            // Add a Rigidbody to the pea (for basic physics)
            Rigidbody rb = pea.AddComponent<Rigidbody>();

            // Set the pea's velocity to move forward
            rb.velocity = Vector3.forward * 10f;

            // Destroy the pea after a few seconds (optional)
            Destroy(pea, 2f);
        }
    }
}
