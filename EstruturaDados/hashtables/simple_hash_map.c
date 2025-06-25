#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUCKET_COUNT 10
#define MAX_KEY_LEN 16
#define MAX_VAL_LEN 32

typedef struct Entry {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    struct Entry* next;
} Entry;

typedef struct {
    Entry* buckets[BUCKET_COUNT];
} SimpleHashMap;

unsigned int hashFunction(const char* key) {
    unsigned int sum = 0;
    for (int i = 0; key[i] != '\0'; i++) {
        if (key[i] >= '0' && key[i] <= '9') {
            sum += key[i] - '0';
        }
    }
    return sum % BUCKET_COUNT;
}

void initHashMap(SimpleHashMap* map) {
    for (int i = 0; i < BUCKET_COUNT; i++) {
        map->buckets[i] = NULL;
    }
}

void put(SimpleHashMap* map, const char* key, const char* value) {
    unsigned int index = hashFunction(key);
    Entry* current = map->buckets[index];
    
    // Update value if key already exists
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            strncpy(current->value, value, MAX_VAL_LEN - 1);
            current->value[MAX_VAL_LEN - 1] = '\0';
            return;
        }
        current = current->next;
    }
    
    // Add new key-value pair
    Entry* newEntry = (Entry*)malloc(sizeof(Entry));
    strncpy(newEntry->key, key, MAX_KEY_LEN - 1);
    newEntry->key[MAX_KEY_LEN - 1] = '\0';
    strncpy(newEntry->value, value, MAX_VAL_LEN - 1);
    newEntry->value[MAX_VAL_LEN - 1] = '\0';
    newEntry->next = map->buckets[index];
    map->buckets[index] = newEntry;
}

const char* get(SimpleHashMap* map, const char* key) {
    unsigned int index = hashFunction(key);
    Entry* current = map->buckets[index];
    
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    
    return NULL; // Key not found
}

void removeEntry(SimpleHashMap* map, const char* key) {
    unsigned int index = hashFunction(key);
    Entry* current = map->buckets[index];
    Entry* prev = NULL;
    
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            if (prev != NULL) {
                prev->next = current->next;
            } else {
                map->buckets[index] = current->next;
            }
            free(current);
            return;
        }
        prev = current;
        current = current->next;
    }
}

void freeHashMap(SimpleHashMap* map) {
    for (int i = 0; i < BUCKET_COUNT; i++) {
        Entry* current = map->buckets[i];
        while (current != NULL) {
            Entry* temp = current;
            current = current->next;
            free(temp);
        }
    }
}

void printHashMap(SimpleHashMap* map) {
    printf("Hash Map Contents:\n");
    for (int i = 0; i < BUCKET_COUNT; i++) {
        Entry* current = map->buckets[i];
        printf("Bucket %d: ", i);
        while (current != NULL) {
            printf("(%s: %s) ", current->key, current->value);
            current = current->next;
        }
        printf("\n");
    }
}

int main() {
    SimpleHashMap map;
    initHashMap(&map);

    put(&map, "123-4567", "Charlotte");
    put(&map, "123-4568", "Thomas");
    put(&map, "123-4569", "Jens");
    put(&map, "123-4570", "Peter");
    put(&map, "123-4571", "Lisa");
    put(&map, "123-4672", "Adele");
    put(&map, "123-4573", "Michaela");
    put(&map, "123-6574", "Bob");

    printHashMap(&map);

    // Demonstrate get and put
    printf("\nName associated with '123-4570': %s\n", get(&map, "123-4570"));
    printf("Updating the name for '123-4570' to 'James'.");
    put(&map, "123-4570", "James");
    printf("\nName associated with '123-4570': %s\n", get(&map, "123-4570"));

    freeHashMap(&map);
    return 0;
}
