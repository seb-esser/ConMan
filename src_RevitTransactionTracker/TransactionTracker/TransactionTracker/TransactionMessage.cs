namespace TransactionTracker
{
    public class TransactionMessage
    {
        public string TransactionType;
        public int ElementId;
        public string ElementUniqueId;
        public string TransactionName;
        public string ElementName;

        public TransactionMessage(string transactionType, int elementId, string elementName, string elementUniqueId = "unknown")
        {
            TransactionType = transactionType;
            ElementId = elementId;
            ElementUniqueId = elementUniqueId;
            
            ElementName = elementName;
        }
    }


}