using System;
using System.Collections.Generic;
using Autodesk.Revit.UI;

namespace RevitVersionControllRibbon
{
    public class VersionControlRibbon : IExternalApplication
    {
        public Result OnStartup(UIControlledApplication application)
        {
            // Create a custom ribbon tab
            String tabName = "Version Control";
            application.CreateRibbonTab(tabName);

            // Create two push buttons
            PushButtonData button1 = new PushButtonData("Snapshot", "Create Snapshot",
                @"C:\Users\ga38hep\dev\consistencyManager\src_designTracker\src_RevitTransactionTracker\TransactionTracker\CommitAddin\bin\Debug\CommitAddin.dll", "CommitAddin.CommitAddin.Execute");
            //button1.LargeImage = "";
            //button1.Image = BmpImageSource(); 

            //PushButtonData button2 = new PushButtonData("Button2", "My Button #2",
            //    @"C:\ExternalCommands.dll", "Revit.Test.Command2");

            // Create a ribbon panel
            RibbonPanel m_projectPanel = application.CreateRibbonPanel(tabName, "Snapshot tools");

            // Add the buttons to the panel
            List<RibbonItem> projectButtons = new List<RibbonItem>();
            projectButtons.AddRange(new[] {m_projectPanel.AddItem(button1)});

            return Result.Succeeded;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            return Result.Succeeded;
        }
    }
}
