using Autodesk.Revit.DB;

namespace TransactionTracker
{
    public class ElementCopy
    {
        public int id;
        public string name;
        public string uniqueId;

        /// <summary>
        /// Constructor with extracted params
        /// </summary>
        /// <param name="id"></param>
        /// <param name="name"></param>
        /// <param name="uniqueId"></param>
        public ElementCopy(int id, string name, string uniqueId)
        {
            this.id = id;
            this.name = name;
            this.uniqueId = uniqueId;
        }

        /// <summary>
        /// constructor with Revit element
        /// </summary>
        /// <param name="element"></param>
        public ElementCopy(Element element)
        {
            this.id = element.Id.IntegerValue;
            this.name = element.Name;
            this.uniqueId = element.UniqueId;
        }

    }
}