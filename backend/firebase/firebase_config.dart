import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';

Future initFirebase() async {
  if (kIsWeb) {
    await Firebase.initializeApp(
        options: FirebaseOptions(
            apiKey: "AIzaSyAuYJkXxnJZ6eAaGwIAu_PlMc-p4Vn_zJc",
            authDomain: "blind-navigation-8fbmw1.firebaseapp.com",
            projectId: "blind-navigation-8fbmw1",
            storageBucket: "blind-navigation-8fbmw1.firebasestorage.app",
            messagingSenderId: "228634013055",
            appId: "1:228634013055:web:184375863a157fe2fbfe4a"));
  } else {
    await Firebase.initializeApp();
  }
}
