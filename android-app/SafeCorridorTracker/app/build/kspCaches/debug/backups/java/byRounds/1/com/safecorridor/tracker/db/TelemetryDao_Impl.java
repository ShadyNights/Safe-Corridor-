package com.safecorridor.tracker.db;

import android.database.Cursor;
import androidx.annotation.NonNull;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class TelemetryDao_Impl implements TelemetryDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<TelemetryPoint> __insertionAdapterOfTelemetryPoint;

  private final SharedSQLiteStatement __preparedStmtOfDelete;

  public TelemetryDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfTelemetryPoint = new EntityInsertionAdapter<TelemetryPoint>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR ABORT INTO `telemetry_queue` (`id`,`timestamp`,`lat`,`lng`,`speed`,`isMock`,`sent`) VALUES (nullif(?, 0),?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TelemetryPoint entity) {
        statement.bindLong(1, entity.getId());
        statement.bindLong(2, entity.getTimestamp());
        statement.bindDouble(3, entity.getLat());
        statement.bindDouble(4, entity.getLng());
        statement.bindDouble(5, entity.getSpeed());
        final int _tmp = entity.isMock() ? 1 : 0;
        statement.bindLong(6, _tmp);
        final int _tmp_1 = entity.getSent() ? 1 : 0;
        statement.bindLong(7, _tmp_1);
      }
    };
    this.__preparedStmtOfDelete = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM telemetry_queue WHERE id = ?";
        return _query;
      }
    };
  }

  @Override
  public void insert(final TelemetryPoint point) {
    __db.assertNotSuspendingTransaction();
    __db.beginTransaction();
    try {
      __insertionAdapterOfTelemetryPoint.insert(point);
      __db.setTransactionSuccessful();
    } finally {
      __db.endTransaction();
    }
  }

  @Override
  public void delete(final long id) {
    __db.assertNotSuspendingTransaction();
    final SupportSQLiteStatement _stmt = __preparedStmtOfDelete.acquire();
    int _argIndex = 1;
    _stmt.bindLong(_argIndex, id);
    try {
      __db.beginTransaction();
      try {
        _stmt.executeUpdateDelete();
        __db.setTransactionSuccessful();
      } finally {
        __db.endTransaction();
      }
    } finally {
      __preparedStmtOfDelete.release(_stmt);
    }
  }

  @Override
  public List<TelemetryPoint> getUnsent() {
    final String _sql = "SELECT * FROM telemetry_queue WHERE sent = 0 ORDER BY timestamp ASC LIMIT 50";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    __db.assertNotSuspendingTransaction();
    final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
    try {
      final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
      final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
      final int _cursorIndexOfLat = CursorUtil.getColumnIndexOrThrow(_cursor, "lat");
      final int _cursorIndexOfLng = CursorUtil.getColumnIndexOrThrow(_cursor, "lng");
      final int _cursorIndexOfSpeed = CursorUtil.getColumnIndexOrThrow(_cursor, "speed");
      final int _cursorIndexOfIsMock = CursorUtil.getColumnIndexOrThrow(_cursor, "isMock");
      final int _cursorIndexOfSent = CursorUtil.getColumnIndexOrThrow(_cursor, "sent");
      final List<TelemetryPoint> _result = new ArrayList<TelemetryPoint>(_cursor.getCount());
      while (_cursor.moveToNext()) {
        final TelemetryPoint _item;
        final long _tmpId;
        _tmpId = _cursor.getLong(_cursorIndexOfId);
        final long _tmpTimestamp;
        _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
        final double _tmpLat;
        _tmpLat = _cursor.getDouble(_cursorIndexOfLat);
        final double _tmpLng;
        _tmpLng = _cursor.getDouble(_cursorIndexOfLng);
        final float _tmpSpeed;
        _tmpSpeed = _cursor.getFloat(_cursorIndexOfSpeed);
        final boolean _tmpIsMock;
        final int _tmp;
        _tmp = _cursor.getInt(_cursorIndexOfIsMock);
        _tmpIsMock = _tmp != 0;
        final boolean _tmpSent;
        final int _tmp_1;
        _tmp_1 = _cursor.getInt(_cursorIndexOfSent);
        _tmpSent = _tmp_1 != 0;
        _item = new TelemetryPoint(_tmpId,_tmpTimestamp,_tmpLat,_tmpLng,_tmpSpeed,_tmpIsMock,_tmpSent);
        _result.add(_item);
      }
      return _result;
    } finally {
      _cursor.close();
      _statement.release();
    }
  }

  @Override
  public int getCount() {
    final String _sql = "SELECT COUNT(*) FROM telemetry_queue";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    __db.assertNotSuspendingTransaction();
    final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
    try {
      final int _result;
      if (_cursor.moveToFirst()) {
        _result = _cursor.getInt(0);
      } else {
        _result = 0;
      }
      return _result;
    } finally {
      _cursor.close();
      _statement.release();
    }
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
