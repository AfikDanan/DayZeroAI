#!/usr/bin/env python3
"""
Test audio generation using existing script
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.audio_generator import AudioGenerator

def parse_script_file(script_path):
    """Parse the script file and extract speaker/text pairs"""
    script = []
    
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the script section
    in_script_section = False
    for line in lines:
        line = line.strip()
        
        if line == "SCRIPT:" or line.startswith("-----"):
            in_script_section = True
            continue
        
        if not in_script_section or not line:
            continue
        
        if line.startswith("Total script lines:"):
            break
        
        # Parse numbered lines like "1. ALEX:" or just "ALEX:"
        if ':' in line:
            if '. ' in line and line.split('. ')[0].isdigit():
                # Format: "1. ALEX: text"
                parts = line.split('. ', 1)
                speaker_and_text = parts[1]
            else:
                # Format: "ALEX: text" (continuation lines)
                speaker_and_text = line
            
            if ':' in speaker_and_text:
                speaker_part, text = speaker_and_text.split(':', 1)
                speaker = speaker_part.strip().lower()
                text = text.strip()
                
                # Convert speaker names to host1/host2
                if speaker == 'alex':
                    speaker = 'host1'
                elif speaker == 'jordan':
                    speaker = 'host2'
                
                if text and speaker in ['host1', 'host2']:
                    script.append((speaker, text))
    
    return script

def test_audio_generation():
    """Test audio generation using existing script"""
    print("🎵 Testing Audio Generation from Existing Script")
    print("=" * 60)
    
    # Find the script file
    script_path = Path("dev_output/direct_test_1760281910/script.txt")
    
    if not script_path.exists():
        print(f"❌ Script file not found: {script_path}")
        return False
    
    print(f"📄 Using script file: {script_path}")
    
    try:
        # Parse the script
        print("📝 Parsing script...")
        script = parse_script_file(script_path)
        print(f"✅ Parsed {len(script)} script lines")
        
        # Show first few lines
        print("\n📋 Script preview:")
        for i, (speaker, text) in enumerate(script[:3], 1):
            speaker_name = "Alex" if speaker == "host1" else "Jordan"
            print(f"   {i}. {speaker_name}: {text[:60]}...")
        
        if len(script) > 3:
            print(f"   ... and {len(script) - 3} more lines")
        
        # Create output directory
        output_dir = Path("dev_output/audio_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📁 Output directory: {output_dir}")
        
        # Initialize audio generator
        print("\n🎵 Initializing audio generator...")
        audio_gen = AudioGenerator()
        print("✅ Audio generator ready")
        
        # Generate audio
        print("\n🚀 Generating audio...")
        print("⏳ This may take a few minutes...")
        
        audio_path = audio_gen.generate_audio(script, output_dir)
        
        # Check if audio was created
        if audio_path.exists():
            file_size = audio_path.stat().st_size
            duration = audio_gen.get_audio_duration(audio_path)
            
            print(f"✅ Audio generated successfully!")
            print(f"📄 Audio file: {audio_path}")
            print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"⏱️ Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            
            return True
        else:
            print(f"❌ Audio file not created: {audio_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🎯 Audio Generation Test")
    print("This test uses an existing script to generate audio with Google Cloud TTS")
    print()
    
    if test_audio_generation():
        print("\n" + "=" * 60)
        print("🎉 AUDIO GENERATION SUCCESSFUL!")
        print("=" * 60)
        print("✅ Google Cloud Text-to-Speech is working")
        print("✅ Audio generation pipeline is functional")
        print("✅ Dual-host voice synthesis working")
        print()
        print("🎧 You can now listen to the generated audio file!")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ AUDIO GENERATION FAILED")
        print("=" * 60)
        print("Check the error messages above for details")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)