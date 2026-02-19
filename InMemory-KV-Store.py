# # Questions 
# 1. Do we have throughput requirements? 
# 1. Do we have memory limits? - Yes, memory cannot exceed MAX_MEMORY
# 1. Do we want to copy to disk asynchronously? - Yes but handle that later 

# KVStore - Multiple threads can call to read or write to this. 
# Gets are clean reads that do not write anything
# To allow for maximum throughput, we can implement a ReaderWriter lock where many different readers can read at a time but only one writer can write and readers stop reading. 

# To copy to disk asynchronously, we can use a background thread that scans for updated to the data and copies it over. We can store the updates in a separate data store becuase we dont not want the async background thread to compete with readers and writers. 
# We need to have two separate locks for the two different data stores. 

# If we just have one lock on the whole table that would be a global lock and generally something that we want to avoid because if we have many different writers/readers, we will see increased latency as we make writes happen. 
# 1. Could use Sharding and a lock per shard so that we can reduce contention on the same data store. 
#  -> We could use lock striping with one dictionary. However, this is not the most safe because if your insert triggers a resize, then the dictionary/hashtable internally increases its size and rehashes everything so your lock is no longer protecting the right keys. Therefore, another thread who thought it had locked the datastructure could - write to the old table and not get copied over or corrupt the internal datastructures. 
#  -> In python GIL protects writes but generally if that weren't the case we could run into issues
# 2. We could use per key locks that are stored in a separate datastore so that we acquire the lock and then make updates to a key. However, adding a new entry would need to lock the whole table. 
# 3. We could do copy-on-write where for reads, we can go ahead with no locks. For writes, we copy the data store, make the update and write it back. Memory usage will spike for every update.
# -> CAS - compare adn swap - make sure that the reference is still the same.

# Deadlocks happen under a few conditions: 
# 1. Mutual exclusion 
# 2. Hold and wait
# 3. No preemption
# 4. Circular dependency  
# We need to make sure we're not falling into these. 
# If we have multiple locks that are being acquired, we should have a global ordering for them
# We should make sure that the locks are protecting only critical logic and additional processing can be done outside . 

# Python specific - cannot reacquire lock in the same thread unless it is a RLock. Therefore, make sure that that is not happening.

# Memory limits: What do we do when we hit the memory limit? 
# 1. Evict from KV store - LRU? If we do an LRU, this would mean we would need to keep track of when elements have been accessed and maintain ordering. Also, we should not use a reader-writer lock because we are now modifying on reads. If we allow multiple readers, we could see inconsistent state with the ordering of the elements for LRU. 
# 2. 

# You could also think about lock-free reads using copy-on-write or versioned data structures to reduce reader contention.

# class ReaderWriterLock:
#     def __init__(self):
#         pass

