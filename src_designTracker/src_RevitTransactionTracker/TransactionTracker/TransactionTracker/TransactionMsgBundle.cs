using System.Collections.Generic;

namespace TransactionTracker
{
    public class TransactionMsgBundle
    {
        public List<TransactionMessage> MsgBundle;

        /// <summary>
        /// default constructor
        /// </summary>
        public TransactionMsgBundle()
        {
            MsgBundle = new List<TransactionMessage>(); 
        }

        /// <summary>
        /// adds a transaction message to the bundle
        /// </summary>
        /// <param name="msg"></param>
        public void AddMessage(TransactionMessage msg)
        {
            MsgBundle.Add(msg);
        }
    }
}