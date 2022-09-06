using System.Collections.Generic;

namespace CommitAddin
{
    public class Snapshot
    {
        public List<ObjectBucket> Bucket;

        public Snapshot(List<ObjectBucket> bucket)
        {
            this.Bucket = bucket;
        }
    }
}