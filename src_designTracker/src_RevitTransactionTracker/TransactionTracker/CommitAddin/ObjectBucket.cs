namespace CommitAddin
{
    public class ObjectBucket
    {
        public int ElementId { get; set;  }
        public string ElementName { get; set; }
        public string ObjectGuid { get; set; }
        public string VersionGuid { get; set; }

        public ObjectBucket(int elementId, string elementName, string objectGuid, string versionGuid)
        {
            ElementId = elementId;
            ElementName = elementName;
            ObjectGuid = objectGuid;
            VersionGuid = versionGuid;
        }
    }
}