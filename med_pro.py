import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

void main() {
  runApp(MyApp());
}

final notifications = FlutterLocalNotificationsPlugin();

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String lang = "uz";
  String result = "";
  TextEditingController controller = TextEditingController();

  Future<void> fetchData(String drug) async {
    final apiKey = "SEN_API_KEY"; // ⚠️ o‘zing qo‘y
    final prompt = "$drug haqida qisqa: tarkibi, dozasi, foydasi, zarari ($lang tilida)";

    final res = await http.post(
      Uri.parse("https://api.openai.com/v1/chat/completions"),
      headers: {
        "Authorization": "Bearer $apiKey",
        "Content-Type": "application/json"
      },
      body: jsonEncode({
        "model": "gpt-4o-mini",
        "messages": [
          {"role": "user", "content": prompt}
        ]
      }),
    );

    final data = jsonDecode(res.body);
    setState(() {
      result = data['choices'][0]['message']['content'];
    });
  }

  Widget section(String title, String text) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
        SizedBox(height: 5),
        Text(text),
        SizedBox(height: 10),
      ],
    );
  }

  Future<void> scheduleNotification() async {
    await notifications.show(
      0,
      "MedAssist",
      lang == "uz"
          ? "Doringizni iching"
          : lang == "ru"
              ? "Примите лекарство"
              : "Take your medicine",
      NotificationDetails(
        android: AndroidNotificationDetails("id", "channel"),
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    notifications.initialize(
      InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // fon o‘zgarmaydi
      appBar: AppBar(
        title: Text("MedAssist Pro"),
      ),
      body: Padding(
        padding: EdgeInsets.all(12),
        child: ListView(
          children: [
            Text("⚠️ Shifokor bilan maslahatlash"),

            TextField(controller: controller),

            Row(
              children: [
                ElevatedButton(
                    onPressed: () => setState(() => lang = "uz"),
                    child: Text("UZ")),
                ElevatedButton(
                    onPressed: () => setState(() => lang = "ru"),
                    child: Text("RU")),
                ElevatedButton(
                    onPressed: () => setState(() => lang = "en"),
                    child: Text("EN")),
              ],
            ),

            ElevatedButton(
              onPressed: () => fetchData(controller.text),
              child: Text("Qidirish"),
            ),

            SizedBox(height: 10),

            Text(result),

            SizedBox(height: 20),

            ElevatedButton(
              onPressed: scheduleNotification,
              child: Text("Eslatma qo‘shish"),
            ),

            SizedBox(height: 20),
            Text("⚠️ Har doim shifokor bilan maslahat qiling"),
          ],
        ),
      ),
    );
  }
}
