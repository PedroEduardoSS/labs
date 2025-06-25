#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUCKET_COUNT 10
#define MAX_STRING_LENGTH 256 // Define a maximum string length

typedef struct Node {
    char value[MAX_STRING_LENGTH]; // Use a fixed-size array for values
    struct Node* next;
} Node;

typedef struct {
    Node* buckets[BUCKET_COUNT];
} SimpleHashSet;

unsigned int hashFunction(const char* value) {
    unsigned int hash = 0;
    while (*value) {
        hash = (hash + *value++) % BUCKET_COUNT;
    }
    return hash;
}

void initHashSet(SimpleHashSet* set) {
    for (int i = 0; i < BUCKET_COUNT; i++) {
        set->buckets[i] = NULL;
    }
}

int contains(SimpleHashSet *set, const char *value) {
    unsigned int index = hashFunction(value);
    Node *node = set->buckets[index];
    while (node != NULL) {
        if (strcmp(node->value, value) == 0) {
            return 1; // Found
        }
        node = node->next;
    }
    return 0; // Not found
}

void removeValue(SimpleHashSet *set, const char *value) {
    unsigned int index = hashFunction(value);
    Node **node = &(set->buckets[index]);
    while (*node != NULL) {
        if (strcmp((*node)->value, value) == 0) {
            Node *toDelete = *node;
            *node = (*node)->next;
            free(toDelete); // Just free the node, not toDelete->value
            return; // Value removed
        }
        node = &((*node)->next);
    }
}

void add(SimpleHashSet* set, const char* value) {
    unsigned int index = hashFunction(value);
    
    // Check if the value already exists to avoid duplicates
    Node* current = set->buckets[index];
    while (current != NULL) {
        if (strcmp(current->value, value) == 0) {
            // Value already exists, do not add again
            return;
        }
        current = current->next;
    }
    
    // Add new value
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) return; // Handle malloc failure
    
    strncpy(newNode->value, value, MAX_STRING_LENGTH);
    newNode->value[MAX_STRING_LENGTH - 1] = '\0'; // Ensure null-termination
    newNode->next = set->buckets[index];
    set->buckets[index] = newNode;
}

void printHashSet(SimpleHashSet *set) {
    printf("Hash Set Contents:\n");
    for (int i = 0; i < BUCKET_COUNT; i++) {
        Node *node = set->buckets[i];
        printf("Bucket %d: ", i);
        while (node) {
            printf("%s ", node->value);
            node = node->next;
        }
        printf("\n");
    }
}

int main() {
    SimpleHashSet hashSet;
    initHashSet(&hashSet);

    add(&hashSet, "Charlotte");
    add(&hashSet, "Thomas");
    add(&hashSet, "Jens");
    add(&hashSet, "Peter");
    add(&hashSet, "Lisa");
    add(&hashSet, "Adele");
    add(&hashSet, "Michaela");
    add(&hashSet, "Bob");

    printHashSet(&hashSet);

    printf("\n'Peter' is in the set: %s\n", contains(&hashSet, "Peter") ? "true" : "false");
    printf("Removing 'Peter'\n");
    removeValue(&hashSet, "Peter");
    printf("'Peter' is in the set: %s\n", contains(&hashSet, "Peter") ? "true" : "false");
    printf("'Adele' has hash code: %u\n", hashFunction("Adele"));

    // Free memory, omitted for brevity
    return 0;
}