namespace TransactionTracker
{
    public class TransactionMessage
    {
        public string TransactionType;
        public int ElementId;
        public string ElementUniqueId;
        public string ElementName;
        public string IfcGuid;

        public TransactionMessage(string transactionType, int elementId, string elementName, string elementUniqueId = "unknown", string ifcGuid = "n/a")
        {
            TransactionType = transactionType;
            ElementId = elementId;
            ElementUniqueId = elementUniqueId;
            
            ElementName = elementName;
            IfcGuid = ifcGuid;
        }
    }


}