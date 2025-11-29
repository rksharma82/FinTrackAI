import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

const FileUpload = ({ onUploadSuccess }) => {
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFiles(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFiles(e.target.files[0]);
        }
    };

    const handleFiles = async (file) => {
        setUploading(true);
        setMessage(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post('/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setMessage({ type: 'success', text: `Successfully processed ${response.data.count} transactions!` });
            if (onUploadSuccess) onUploadSuccess();
        } catch (error) {
            console.error("Upload error:", error);
            setMessage({ type: 'error', text: error.response?.data?.detail || "Upload failed. Please try again." });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto mb-8">
            <div
                className={`relative p-8 border-2 border-dashed rounded-xl transition-all duration-200 ease-in-out text-center
          ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-white hover:border-slate-400'}
          ${uploading ? 'opacity-50 cursor-wait' : 'cursor-pointer'}
        `}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    onChange={handleChange}
                    disabled={uploading}
                />

                <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="p-4 bg-blue-100 rounded-full text-blue-600">
                        <Upload size={32} />
                    </div>
                    <div>
                        <p className="text-lg font-medium text-slate-700">
                            {uploading ? "Processing..." : "Drop your statement here"}
                        </p>
                        <p className="text-sm text-slate-500 mt-1">
                            Supports CSV, Excel, or Text files
                        </p>
                    </div>
                </div>
            </div>

            {message && (
                <div className={`mt-4 p-4 rounded-lg flex items-center gap-3 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                    }`}>
                    {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                    <span>{message.text}</span>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
