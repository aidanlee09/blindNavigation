// Automatic FlutterFlow imports
import '/backend/backend.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'index.dart'; // Imports other custom widgets
import '/flutter_flow/custom_functions.dart'; // Imports custom functions
import 'package:flutter/material.dart';
// Begin custom widget code
// DO NOT REMOVE OR MODIFY THE CODE ABOVE!

import 'dart:convert';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:firebase_core/firebase_core.dart';
import 'dart:io';

class CameraPhoto extends StatefulWidget {
  const CameraPhoto({Key? key, this.width, this.height}) : super(key: key);

  final double? width;
  final double? height;

  @override
  _CameraPhotoState createState() => _CameraPhotoState();
}

class _CameraPhotoState extends State<CameraPhoto> {
  CameraController? controller;
  late Future<List<CameraDescription>> _cameras;

  @override
  void initState() {
    super.initState();
    _cameras = availableCameras();
  }

  @override
  void didUpdateWidget(covariant CameraPhoto oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (FFAppState().makePhoto) {
      controller!.takePicture().then((file) async {
        try {
          // Store local file path in AppState (for UI reference)
          FFAppState().update(() {
            FFAppState().capturedImagePath = file.path;
          });

          // Upload image to Firebase Storage
          String fileName =
              "photos/${DateTime.now().millisecondsSinceEpoch}.jpg";
          Reference storageRef = FirebaseStorage.instance.ref().child(fileName);
          UploadTask uploadTask = storageRef.putFile(File(file.path));

          // Get the download URL after successful upload
          TaskSnapshot taskSnapshot = await uploadTask;
          String downloadUrl = await taskSnapshot.ref.getDownloadURL();

          debugPrint('Image uploaded to Firebase: $downloadUrl');

          // Store image download URL in AppState for later use
          FFAppState().update(() {
            FFAppState().imageDownloadUrl = downloadUrl;
          });
        } catch (error) {
          debugPrint('Error during Firebase upload: $error');
        } finally {
          // Reset the photo flag regardless of upload success
          FFAppState().update(() {
            FFAppState().makePhoto = false;
          });
        }
      }).catchError((error) {
        debugPrint("Error taking picture: $error");
      });
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<CameraDescription>>(
      future: _cameras,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          if (snapshot.hasData && snapshot.data!.isNotEmpty) {
            // Find the back camera
            CameraDescription? backCamera = snapshot.data!.firstWhere(
              (camera) => camera.lensDirection == CameraLensDirection.back,
              orElse: () =>
                  snapshot.data!.first, // Use first available if no back camera
            );

            if (controller == null || !controller!.value.isInitialized) {
              controller = CameraController(backCamera, ResolutionPreset.max);

              controller!.initialize().then((_) {
                if (!mounted) return;
                setState(() {});
              }).catchError((error) {
                debugPrint("Camera initialization error: $error");
              });
            }

            return controller!.value.isInitialized
                ? MaterialApp(home: CameraPreview(controller!))
                : Center(child: CircularProgressIndicator());
          } else {
            return Center(child: Text('No cameras available.'));
          }
        } else {
          return Center(child: CircularProgressIndicator());
        }
      },
    );
  }
}
