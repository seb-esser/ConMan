namespace TUMCMS_SE_ModelGraphGen
{
    public class InstanceModel2Neo4jParser
    {
        private string SourceLocation { get; set; }
        private string TargetLocation { get; set; }

        /// <summary>
        /// 
        /// </summary>
        public InstanceModel2Neo4jParser()
        {
        }

        public InstanceModel2Neo4jParser(string sourceLocation)
        {
            SourceLocation = sourceLocation;
        }


        public void CreateNeo4jScript()
        {
            var sourceFile = SourceLocation;
            var modelType = "IFC";
            // switch format

            switch (modelType)
            {
                case "IFC":

                    break;

                case "PlanPro":

                    break;

                case "RailML":

                    break;

                default:
                    break;
            }
        }
    }
}
